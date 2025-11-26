from google.cloud import vision
from google.cloud import storage
from PIL import Image
import io
import logging
from typing import Dict, List, Optional, Tuple
import asyncio
from functools import wraps

from app.config import settings

logger = logging.getLogger(__name__)

def async_wrap(func):
    """Decorator to wrap synchronous functions to run in executor"""
    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return run

class OCRService:
    def __init__(self):
        self.vision_client = vision.ImageAnnotatorClient()
        self.storage_client = storage.Client()
    
    async def extract_document_data(self, image_content: bytes) -> Dict:
        """Extract data from document using OCR"""
        try:
            # Preprocess image
            processed_content = await self.preprocess_image(image_content)
            
            # Extract text
            full_text, confidence = await self.extract_text_from_image(processed_content)
            
            if not full_text:
                logger.warning("No text extracted from document")
                return {
                    'raw_text': '',
                    'confidence': 0.0,
                    'pages': 0,
                    'blocks': []
                }
            
            # Detect document type
            doc_type = await self.detect_document_type(full_text)
            
            return {
                'raw_text': full_text,
                'confidence': confidence,
                'document_type': doc_type,
                'pages': 1,
                'blocks': [],
                'text_length': len(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error extracting document data: {str(e)}")
            raise e
    
    async def extract_text_from_image(self, image_content: bytes) -> Tuple[str, float]:
        """Extract text from image using Google Cloud Vision API"""
        try:
            # Wrap synchronous Google Cloud Vision API call
            result = await self._call_vision_api(image_content)
            return result
            
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e
    
    @async_wrap
    def _call_vision_api(self, image_content: bytes) -> Tuple[str, float]:
        """Synchronous wrapper for Vision API call"""
        image = vision.Image(content=image_content)
        
        # Perform OCR
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            return "", 0.0
        
        # Get full text (first annotation contains all text)
        full_text = texts[0].description
        
        # Calculate average confidence
        confidence = self._calculate_confidence(texts[1:])  # Skip first (full text)
        
        if response.error.message:
            raise Exception(f"OCR API error: {response.error.message}")
        
        logger.info(f"OCR completed with confidence: {confidence}")
        return full_text, confidence
    
    async def extract_text_from_pdf(self, pdf_content: bytes) -> Tuple[str, float]:
        """Extract text from PDF using Google Cloud Vision API"""
        try:
            # For MVP, we'll treat PDF as image
            # In production, you'd use Document AI for better PDF processing
            return await self.extract_text_from_image(pdf_content)
        except Exception as e:
            logger.error(f"PDF OCR error: {str(e)}")
            raise e
    
    async def preprocess_image(self, image_content: bytes) -> bytes:
        """Preprocess image for better OCR results"""
        try:
            # Run preprocessing in executor to avoid blocking
            result = await self._preprocess_sync(image_content)
            return result
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}")
            return image_content  # Return original if preprocessing fails
    
    @async_wrap
    def _preprocess_sync(self, image_content: bytes) -> bytes:
        """Synchronous image preprocessing"""
        # Open image with PIL
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (maintain aspect ratio)
        max_size = 2048
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save processed image
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=95, optimize=True)
        return output.getvalue()
    
    def _calculate_confidence(self, word_annotations: List) -> float:
        """Calculate average confidence from word annotations"""
        if not word_annotations:
            return 0.0
        
        total_confidence = 0.0
        word_count = 0
        
        for annotation in word_annotations:
            if hasattr(annotation, 'confidence'):
                total_confidence += annotation.confidence
                word_count += 1
        
        return total_confidence / word_count if word_count > 0 else 0.7  # Default reasonable confidence
    
    async def detect_document_type(self, text: str) -> str:
        """Detect document type based on extracted text"""
        text_lower = text.lower()
        
        # Common medical test patterns
        if any(term in text_lower for term in ['hemoglobin', 'hb', 'rbc', 'wbc', 'platelet']):
            return "Blood Test"
        elif any(term in text_lower for term in ['cholesterol', 'ldl', 'hdl', 'triglyceride']):
            return "Lipid Panel"
        elif any(term in text_lower for term in ['liver', 'alt', 'ast', 'sgpt', 'sgot', 'bilirubin']):
            return "Liver Function Test"
        elif any(term in text_lower for term in ['glucose', 'sugar', 'hba1c', 'diabetes']):
            return "Diabetes Test"
        elif any(term in text_lower for term in ['thyroid', 'tsh', 't3', 't4']):
            return "Thyroid Function Test"
        elif any(term in text_lower for term in ['kidney', 'creatinine', 'urea', 'bun']):
            return "Kidney Function Test"
        else:
            return "Medical Report"
