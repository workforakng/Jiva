import functions_framework
from google.cloud import vision
from google.cloud import firestore
from google.cloud import storage
import logging
import os
import re
import json
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
vision_client = vision.ImageAnnotatorClient()
firestore_client = firestore.Client()
storage_client = storage.Client()

# Biomarker patterns (simplified version of NLP service)
BIOMARKER_PATTERNS = {
    'hemoglobin': {
        'patterns': [r'hb\s*:?\s*(\d+\.?\d*)\s*(g/dl|gm/dl)'],
        'unit': 'g/dL',
        'range': '12.0-16.0',
        'min': 12.0,
        'max': 16.0
    },
    'blood_sugar': {
        'patterns': [r'glucose\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'],
        'unit': 'mg/dL',
        'range': '70-100',
        'min': 70,
        'max': 100
    },
    'cholesterol': {
        'patterns': [r'cholesterol\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'],
        'unit': 'mg/dL',
        'range': '<200',
        'min': 0,
        'max': 200
    },
    'ldl': {
        'patterns': [r'ldl\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'],
        'unit': 'mg/dL',
        'range': '<100',
        'min': 0,
        'max': 100
    },
    'hdl': {
        'patterns': [r'hdl\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'],
        'unit': 'mg/dL',
        'range': '>40',
        'min': 40,
        'max': 999
    },
    'triglycerides': {
        'patterns': [r'triglycerides\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'],
        'unit': 'mg/dL',
        'range': '<150',
        'min': 0,
        'max': 150
    }
}

@functions_framework.cloud_event
def process_document(cloud_event):
    """
    Cloud Function triggered by Cloud Storage upload.
    Processes medical documents with OCR and NLP.
    
    Args:
        cloud_event: CloudEvent from Cloud Storage
    """
    try:
        # Extract file information from the event
        data = cloud_event.data
        bucket_name = data['bucket']
        file_name = data['name']
        
        logger.info(f"Processing file: gs://{bucket_name}/{file_name}")
        
        # Only process documents in the 'documents/' folder
        if not file_name.startswith('documents/'):
            logger.info(f"Skipping file {file_name} - not in documents folder")
            return
        
        # Extract user ID from path (documents/{user_id}/{filename})
        path_parts = file_name.split('/')
        if len(path_parts) < 3:
            logger.error(f"Invalid file path structure: {file_name}")
            return
        
        user_id = path_parts[1]
        
        # Download the file from Cloud Storage
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        if not blob.exists():
            logger.error(f"File not found: {file_name}")
            return
        
        # Download file content
        file_content = blob.download_as_bytes()
        
        # Perform OCR
        logger.info("Starting OCR processing...")
        ocr_result = perform_ocr(file_content)
        
        if not ocr_result['text']:
            logger.warning(f"No text extracted from {file_name}")
            return
        
        # Extract biomarkers using NLP
        logger.info("Extracting biomarkers...")
        nlp_result = extract_biomarkers(ocr_result['text'])
        
        # Create health record in Firestore
        logger.info("Creating health record in Firestore...")
        record_data = {
            'user_id': user_id,
            'date': nlp_result.get('date', datetime.now().strftime('%Y-%m-%d')),
            'type': nlp_result.get('test_type', 'Medical Document'),
            'facility': nlp_result.get('facility', 'Unknown Facility'),
            'biomarkers': nlp_result.get('biomarkers', {}),
            'original_document': file_name.split('/')[-1],
            'document_url': f"gs://{bucket_name}/{file_name}",
            'ocr_confidence': ocr_result.get('confidence', 0.0),
            'processing_metadata': {
                'processed_at': datetime.utcnow().isoformat(),
                'processor': 'cloud-function',
                'ocr_pages': ocr_result.get('pages', 0),
                'text_length': len(ocr_result.get('text', '')),
                'biomarkers_found': len(nlp_result.get('biomarkers', {}))
            },
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Save to Firestore
        doc_ref = firestore_client.collection('health_records').document()
        doc_ref.set(record_data)
        
        logger.info(f"Health record created: {doc_ref.id}")
        
        # Optionally send notification (implement based on your needs)
        # send_notification(user_id, doc_ref.id, nlp_result)
        
        return {
            'success': True,
            'record_id': doc_ref.id,
            'message': 'Document processed successfully'
        }
        
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        # In production, you might want to write to a dead-letter queue
        return {
            'success': False,
            'error': str(e)
        }


def perform_ocr(image_bytes: bytes) -> Dict[str, Any]:
    """
    Perform OCR on image using Google Cloud Vision API
    
    Args:
        image_bytes: Image content as bytes
        
    Returns:
        Dictionary with extracted text and metadata
    """
    try:
        image = vision.Image(content=image_bytes)
        
        # Perform document text detection
        response = vision_client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")
        
        # Extract full text
        full_text = response.full_text_annotation.text if response.full_text_annotation else ""
        
        # Calculate confidence
        confidence = calculate_ocr_confidence(response)
        
        # Count pages
        pages = len(response.full_text_annotation.pages) if response.full_text_annotation else 0
        
        logger.info(f"OCR completed. Extracted {len(full_text)} characters with {confidence:.2f} confidence")
        
        return {
            'text': full_text,
            'confidence': confidence,
            'pages': pages,
            'language': 'en'  # Could be detected from response
        }
        
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return {
            'text': '',
            'confidence': 0.0,
            'pages': 0,
            'error': str(e)
        }


def calculate_ocr_confidence(response) -> float:
    """Calculate overall confidence score from OCR response"""
    try:
        if not response.text_annotations or len(response.text_annotations) < 2:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        # Skip first annotation (full text)
        for annotation in response.text_annotations[1:]:
            if hasattr(annotation, 'confidence'):
                total_confidence += annotation.confidence
                count += 1
        
        return total_confidence / count if count > 0 else 0.5
        
    except Exception as e:
        logger.warning(f"Error calculating confidence: {e}")
        return 0.5


def extract_biomarkers(text: str) -> Dict[str, Any]:
    """
    Extract biomarkers and medical information from text
    
    Args:
        text: Extracted text from OCR
        
    Returns:
        Dictionary with biomarkers and metadata
    """
    try:
        # Clean text
        cleaned_text = text.lower()
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Extract biomarkers
        biomarkers = {}
        
        for biomarker_name, config in BIOMARKER_PATTERNS.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, cleaned_text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        value = float(match.group(1))
                        unit = match.group(2) if len(match.groups()) > 1 else config['unit']
                        
                        status = determine_status(value, config['min'], config['max'])
                        
                        biomarkers[biomarker_name] = {
                            'value': value,
                            'unit': unit,
                            'range': config['range'],
                            'status': status
                        }
                        
                        break  # Use first match
                    except (ValueError, IndexError):
                        continue
        
        # Extract test type
        test_type = extract_test_type(cleaned_text)
        
        # Extract facility
        facility = extract_facility(cleaned_text)
        
        # Extract date
        test_date = extract_date(cleaned_text)
        
        logger.info(f"Extracted {len(biomarkers)} biomarkers")
        
        return {
            'biomarkers': biomarkers,
            'test_type': test_type,
            'facility': facility,
            'date': test_date,
            'confidence': calculate_extraction_confidence(biomarkers, text)
        }
        
    except Exception as e:
        logger.error(f"Biomarker extraction error: {e}")
        return {
            'biomarkers': {},
            'test_type': 'Unknown',
            'facility': 'Unknown Facility',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'confidence': 0.0
        }


def determine_status(value: float, min_normal: float, max_normal: float) -> str:
    """Determine if value is normal, borderline, or abnormal"""
    if min_normal <= value <= max_normal:
        return 'normal'
    elif (min_normal * 0.9) <= value <= (max_normal * 1.1):
        return 'borderline'
    else:
        return 'abnormal'


def extract_test_type(text: str) -> str:
    """Extract test type from text"""
    test_types = {
        'Complete Blood Count': ['complete blood count', 'cbc', 'hemogram'],
        'Lipid Panel': ['lipid profile', 'lipid panel', 'cholesterol'],
        'Liver Function Test': ['liver function', 'lft', 'hepatic'],
        'Blood Test': ['blood test', 'blood work']
    }
    
    for test_type, keywords in test_types.items():
        if any(keyword in text for keyword in keywords):
            return test_type
    
    return 'Medical Test'


def extract_facility(text: str) -> str:
    """Extract medical facility name"""
    patterns = [
        r'(.*?(?:hospital|clinic|diagnostics|lab|laboratory).*?)(?:\n|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            facility = match.group(1).strip()
            if 5 < len(facility) < 100:
                return facility
    
    return 'Medical Facility'


def extract_date(text: str) -> str:
    """Extract test date from text"""
    date_patterns = [
        r'date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                date_str = match.group(1)
                # Basic date parsing (expand as needed)
                return parse_date(date_str)
            except:
                continue
    
    return datetime.now().strftime('%Y-%m-%d')


def parse_date(date_str: str) -> str:
    """Parse date string to standard format"""
    from datetime import datetime
    
    formats = ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d']
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return datetime.now().strftime('%Y-%m-%d')


def calculate_extraction_confidence(biomarkers: Dict, text: str) -> float:
    """Calculate confidence score for extraction"""
    if not biomarkers:
        return 0.0
    
    biomarker_score = min(len(biomarkers) * 0.2, 1.0)
    text_quality = min(len(text) / 1000, 1.0)
    
    return round((biomarker_score * 0.7 + text_quality * 0.3), 2)


def send_notification(user_id: str, record_id: str, nlp_result: Dict):
    """
    Send notification to user (implement based on your notification system)
    This could use Firebase Cloud Messaging, SendGrid, etc.
    """
    logger.info(f"Notification would be sent to user {user_id} for record {record_id}")
    # Implement notification logic here
    pass
