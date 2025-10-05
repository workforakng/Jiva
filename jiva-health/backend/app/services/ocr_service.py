 
from google.cloud import vision
from google.cloud import storage
from PIL import Image
import io
import logging
from typing import Dict, List, Optional, Tuple

from app.config import settings

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.vision_client = vision.ImageAnnotatorClient()
        self.storage_client = storage.Client()
    
    async def extract_text_from_image(self, image_content: bytes) -> Tuple[str, float]:
        """Extract text from image using Google Cloud Vision API"""
        try:
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
            
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e
    
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
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}")
            return image_content  # Return original if preprocessing fails
    
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
        
        return total_confidence / word_count if word_count > 0 else 0.0
    
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
