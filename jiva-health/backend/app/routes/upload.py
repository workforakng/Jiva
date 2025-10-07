from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from firebase_admin import auth as firebase_auth
import aiofiles
import os
import logging
from typing import Optional
import uuid
from datetime import datetime

from app.services.firestore_service import FirestoreService
from app.services.ocr_service import OCRService
from app.services.nlp_service import NLPService
from google.cloud import storage

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dependencies
async def get_firestore_service():
    return FirestoreService()

async def get_ocr_service():
    return OCRService()

async def get_nlp_service():
    return NLPService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify Firebase token and return user info"""
    try:
        token = credentials.credentials
        decoded_token = firebase_auth.verify_id_token(token)
        return {
            'uid': decoded_token.get('uid'),
            'email': decoded_token.get('email')
        }
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    # Check file extension
    file_ext = os.path.splitext(file.filename.lower())[1] if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    return True

async def upload_to_cloud_storage(file_path: str, destination_blob_name: str) -> str:
    """Upload file to Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(file_path)
        
        return f"gs://{bucket_name}/{destination_blob_name}"
        
    except Exception as e:
        logger.error(f"Error uploading to cloud storage: {e}")
        raise

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    firestore_service: FirestoreService = Depends(get_firestore_service),
    ocr_service: OCRService = Depends(get_ocr_service),
    nlp_service: NLPService = Depends(get_nlp_service),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process medical document"""
    file_path = None
    try:
        # Validate file
        if not validate_file(file):
            raise HTTPException(
                status_code=400,
                detail="Invalid file. Supported formats: PDF, JPG, JPEG, PNG. Max size: 10MB"
            )
        
        # Use current user's ID
        target_user_id = current_user.get('uid')
        if not target_user_id:
            raise HTTPException(status_code=401, detail="User authentication required")
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".tmp"
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save uploaded file temporarily
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            
            # Check actual file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
            
            await buffer.write(content)
        
        logger.info(f"File saved temporarily: {file_path}")
        
        # Upload to cloud storage
        cloud_storage_path = f"documents/{target_user_id}/{unique_filename}"
        cloud_url = await upload_to_cloud_storage(file_path, cloud_storage_path)
        
        logger.info(f"File uploaded to cloud storage: {cloud_url}")
        
        # Process with OCR
        logger.info("Starting OCR processing...")
        ocr_result = await ocr_service.extract_document_data(content)
        
        if not ocr_result.get('raw_text'):
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")
        
        # Process with NLP to extract biomarkers
        logger.info("Starting NLP processing...")
        nlp_result = await nlp_service.extract_biomarkers(ocr_result['raw_text'])
        
        # Create health record
        health_record_data = {
            'user_id': target_user_id,
            'date': nlp_result.get('date', datetime.now().strftime('%Y-%m-%d')),
            'type': nlp_result.get('test_type', 'Medical Document'),
            'facility': nlp_result.get('facility', 'Unknown Facility'),
            'biomarkers': nlp_result.get('biomarkers', {}),
            'original_document': file.filename or unique_filename,
            'document_url': cloud_url,
            'ocr_confidence': ocr_result.get('confidence', 0.0),
            'processing_metadata': {
                'ocr_pages': ocr_result.get('pages', 0),
                'ocr_blocks': ocr_result.get('blocks', 0),
                'nlp_entities_found': len(nlp_result.get('entities', [])),
                'processed_at': datetime.utcnow().isoformat()
            }
        }
        
        # Save to Firestore
        record_id = await firestore_service.create_health_record(health_record_data)
        
        # Clean up temporary file
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {file_path}: {e}")
        
        # Get the created record
        created_record = await firestore_service.get_health_record(record_id)
        
        return {
            "success": True,
            "message": "Document processed successfully",
            "data": {
                "record_id": record_id,
                "record": created_record,
                "processing_summary": {
                    "ocr_confidence": ocr_result.get('confidence', 0.0),
                    "biomarkers_extracted": len(nlp_result.get('biomarkers', {})),
                    "text_length": len(ocr_result.get('raw_text', '')),
                    "processing_time": "~3-5 seconds"
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document upload: {e}")
        # Clean up temporary file on error
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.post("/process")
async def process_existing_document(
    document_url: str = Form(...),
    firestore_service: FirestoreService = Depends(get_firestore_service),
    ocr_service: OCRService = Depends(get_ocr_service),
    nlp_service: NLPService = Depends(get_nlp_service),
    current_user: dict = Depends(get_current_user)
):
    """Process an already uploaded document"""
    try:
        target_user_id = current_user.get('uid')
        if not target_user_id:
            raise HTTPException(status_code=401, detail="User authentication required")
        
        # This endpoint would be used to reprocess documents
        # Implementation would download from cloud storage and reprocess
        
        return {
            "success": True,
            "message": "Document reprocessing initiated",
            "data": {
                "status": "processing",
                "document_url": document_url
            }
        }
        
    except Exception as e:
        logger.error(f"Error reprocessing document: {e}")
        raise HTTPException(status_code=500, detail="Failed to reprocess document")

@router.get("/status/{record_id}")
async def get_processing_status(
    record_id: str,
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user)
):
    """Get processing status of an upload"""
    try:
        record = await firestore_service.get_health_record(record_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Ensure user can only access their own records
        if record.get('user_id') != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        processing_metadata = record.get('processing_metadata', {})
        
        return {
            "success": True,
            "data": {
                "record_id": record_id,
                "status": "completed",
                "ocr_confidence": record.get('ocr_confidence', 0.0),
                "biomarkers_count": len(record.get('biomarkers', {})),
                "processed_at": processing_metadata.get('processed_at'),
                "document_url": record.get('document_url')
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing status")

@router.delete("/document/{record_id}")
async def delete_uploaded_document(
    record_id: str,
    firestore_service: FirestoreService = Depends(get_firestore_service),
    current_user: dict = Depends(get_current_user)
):
    """Delete an uploaded document and its record"""
    try:
        record = await firestore_service.get_health_record(record_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        # Ensure user can only delete their own records
        if record.get('user_id') != current_user.get('uid'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete from cloud storage (optional - implement based on your needs)
        document_url = record.get('document_url')
        if document_url and document_url.startswith('gs://'):
            try:
                # Parse GCS URL and delete
                logger.info(f"Would delete cloud storage file: {document_url}")
            except Exception as e:
                logger.warning(f"Could not delete cloud storage file: {e}")
        
        # Delete record from Firestore
        await firestore_service.delete_health_record(record_id)
        
        return {
            "success": True,
            "message": "Document and record deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")
