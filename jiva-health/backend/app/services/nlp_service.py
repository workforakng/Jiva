import spacy
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from app.config import settings
from app.models.health_record import Biomarker

logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        try:
            self.nlp = spacy.load(settings.spacy_model)
            logger.info(f"Loaded spaCy model: {settings.spacy_model}")
        except OSError:
            logger.error(f"spaCy model {settings.spacy_model} not found")
            raise
    
    async def extract_biomarkers(self, text: str) -> Dict[str, Biomarker]:
        """Extract biomarkers from medical text"""
        try:
            biomarkers = {}
            
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Define biomarker patterns
            patterns = self._get_biomarker_patterns()
            
            for pattern_name, pattern_config in patterns.items():
                matches = self._find_pattern_matches(text, pattern_config)
                
                for match in matches:
                    biomarker = self._create_biomarker(match, pattern_config)
                    if biomarker:
                        biomarkers[pattern_name] = biomarker
            
            logger.info(f"Extracted {len(biomarkers)} biomarkers")
            return biomarkers
            
        except Exception as e:
            logger.error(f"Biomarker extraction error: {str(e)}")
            return {}
    
    async def extract_facility_info(self, text: str) -> str:
        """Extract facility/lab name from text"""
        try:
            # Common lab/hospital name patterns
            lab_patterns = [
                r'(?i)(dr\.?\s+)?([a-z\s]+(?:lab|laboratory|diagnostic|hospital|clinic|medical|healthcare|pathology)(?:\s+[a-z\s]*)?)',
                r'(?i)([a-z\s]+(?:lab|laboratory|diagnostic|hospital|clinic|medical|healthcare|pathology))',
            ]
            
            for pattern in lab_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # Return the first match, cleaned up
                    facility = matches[0] if isinstance(matches[0], str) else matches[0][-1]
                    return facility.strip().title()
            
            return "Unknown Facility"
            
        except Exception as e:
            logger.error(f"Facility extraction error: {str(e)}")
            return "Unknown Facility"
    
    async def extract_test_date(self, text: str) -> str:
        """Extract test date from text"""
        try:
            # Date patterns
            date_patterns = [
                r'(?i)(?:date|dated?):?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(?i)(?:on|date):?\s*(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    date_str = matches[0]
                    # Try to parse and format date
                    try:
                        # Handle different date formats
                        if '/' in date_str or '-' in date_str:
                            # Try different formats
                            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%y', '%d-%m-%y']:
                                try:
                                    parsed_date = datetime.strptime(date_str, fmt)
                                    return parsed_date.strftime('%Y-%m-%d')
                                except ValueError:
                                    continue
                        return date_str
                    except:
                        return date_str
            
            # Return today's date as fallback
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.error(f"Date extraction error: {str(e)}")
            return datetime.now().strftime('%Y-%m-%d')
    
    def _get_biomarker_patterns(self) -> Dict[str, Dict]:
        """Define patterns for common biomarkers"""
        return {
            'hemoglobin': {
                'patterns': [
                    r'(?i)h[ae]moglobin|hgb?:?\s*(\d+\.?\d*)\s*(g/dl|gm/dl|g%)',
                    r'(?i)hb:?\s*(\d+\.?\d*)\s*(g/dl|gm/dl|g%)',
                ],
                'unit': 'g/dL',
                'normal_range': '12.0-16.0',
                'normal_min': 12.0,
                'normal_max': 16.0
            },
            'blood_sugar': {
                'patterns': [
                    r'(?i)(?:blood\s*)?(?:glucose|sugar):?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                    r'(?i)(?:fasting\s*)?(?:glucose|sugar):?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                ],
                'unit': 'mg/dL',
                'normal_range': '70-100',
                'normal_min': 70,
                'normal_max': 100
            },
            'cholesterol': {
                'patterns': [
                    r'(?i)(?:total\s*)?cholesterol:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                ],
                'unit': 'mg/dL',
                'normal_range': '<200',
                'normal_min': 0,
                'normal_max': 200
            },
            'ldl': {
                'patterns': [
                    r'(?i)ldl[-\s]*(?:cholesterol)?:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                ],
                'unit': 'mg/dL',
                'normal_range': '<100',
                'normal_min': 0,
                'normal_max': 100
            },
            'hdl': {
                'patterns': [
                    r'(?i)hdl[-\s]*(?:cholesterol)?:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                ],
                'unit': 'mg/dL',
                'normal_range': '>40',
                'normal_min': 40,
                'normal_max': 999
            },
            'triglycerides': {
                'patterns': [
                    r'(?i)triglycerides?:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                ],
                'unit': 'mg/dL',
                'normal_range': '<150',
                'normal_min': 0,
                'normal_max': 150
            },
            'creatinine': {
                'patterns': [
                    r'(?i)creatinine:?\s*(\d+\.?\d*)\s*(mg/dl|μmol/l)',
                ],
                'unit': 'mg/dL',
                'normal_range': '0.6-1.2',
                'normal_min': 0.6,
                'normal_max': 1.2
            },
            'alt': {
                'patterns': [
                    r'(?i)(?:alt|sgpt):?\s*(\d+\.?\d*)\s*(u/l|iu/l)',
                ],
                'unit': 'U/L',
                'normal_range': '7-45',
                'normal_min': 7,
                'normal_max': 45
            },
            'ast': {
                'patterns': [
                    r'(?i)(?:ast|sgot):?\s*(\d+\.?\d*)\s*(u/l|iu/l)',
                ],
                'unit': 'U/L',
                'normal_range': '8-40',
                'normal_min': 8,
                'normal_max': 40
            }
        }
    
    def _find_pattern_matches(self, text: str, pattern_config: Dict) -> List[Tuple[str, str]]:
        """Find all matches for a biomarker pattern"""
        matches = []
        
        for pattern in pattern_config['patterns']:
            found = re.findall(pattern, text)
            for match in found:
                if isinstance(match, tuple):
                    value, unit = match
                    matches.append((value, unit))
                else:
                    matches.append((match, pattern_config['unit']))
        
        return matches
    
    def _create_biomarker(self, match: Tuple[str, str], pattern_config: Dict) -> Optional[Biomarker]:
        """Create a Biomarker object from a match"""
        try:
            value_str, unit = match
            value = float(value_str)
            
            # Determine status
            status = self._determine_status(value, pattern_config)
            
            return Biomarker(
                value=value,
                unit=pattern_config['unit'],
                range=pattern_config['normal_range'],
                status=status
            )
            
        except (ValueError, KeyError) as e:
            logger.warning(f"Could not create biomarker: {str(e)}")
            return None
    
    def _determine_status(self, value: float, pattern_config: Dict) -> str:
        """Determine if biomarker value is normal, borderline, or abnormal"""
        try:
            normal_min = pattern_config.get('normal_min', 0)
            normal_max = pattern_config.get('normal_max', float('inf'))
            
            if normal_min <= value <= normal_max:
                return 'normal'
            elif value < normal_min * 0.9 or value > normal_max * 1.1:
                return 'abnormal'
            else:
                return 'borderline'
                
        except Exception:
            return 'normal'  # Default to normal if can't determine
