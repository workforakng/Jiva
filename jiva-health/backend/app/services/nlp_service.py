import re
import spacy
import nltk
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Download required NLTK data (run once)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    logger.warning("Could not download NLTK data")

class NLPService:
    """Natural Language Processing service for medical document analysis"""
    
    def __init__(self):
        """Initialize NLP service with spaCy model"""
        try:
            # Load English model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Medical terminology patterns
        self.biomarker_patterns = self._load_biomarker_patterns()
        self.facility_patterns = self._load_facility_patterns()
        self.date_patterns = self._load_date_patterns()
        self.test_type_patterns = self._load_test_type_patterns()
    
    def _load_biomarker_patterns(self) -> Dict[str, Dict]:
        """Load biomarker patterns and normal ranges"""
        return {
            # Blood Test Markers
            'hemoglobin': {
                'patterns': [
                    r'hb\s*:?\s*(\d+\.?\d*)\s*(g/dl|gm/dl|g%)',
                    r'hemoglobin\s*:?\s*(\d+\.?\d*)\s*(g/dl|gm/dl|g%)',
                    r'haemoglobin\s*:?\s*(\d+\.?\d*)\s*(g/dl|gm/dl|g%)'
                ],
                'unit': 'g/dL',
                'normal_range': '12.0-16.0',
                'normal_min': 12.0,
                'normal_max': 16.0
            },
            'blood_sugar': {
                'patterns': [
                    r'glucose\s*:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                    r'blood\s*sugar\s*:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                    r'fasting\s*glucose\s*:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)',
                    r'random\s*glucose\s*:?\s*(\d+\.?\d*)\s*(mg/dl|mmol/l)'
                ],
                'unit': 'mg/dL',
                'normal_range': '70-100',
                'normal_min': 70,
                'normal_max': 100
            },
            'cholesterol': {
                'patterns': [
                    r'total\s*cholesterol\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'cholesterol\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'chol\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'
                ],
                'unit': 'mg/dL',
                'normal_range': '<200',
                'normal_min': 0,
                'normal_max': 200
            },
            'ldl_cholesterol': {
                'patterns': [
                    r'ldl\s*cholesterol\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'ldl\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'low\s*density\s*lipoprotein\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'
                ],
                'unit': 'mg/dL',
                'normal_range': '<100',
                'normal_min': 0,
                'normal_max': 100
            },
            'hdl_cholesterol': {
                'patterns': [
                    r'hdl\s*cholesterol\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'hdl\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'high\s*density\s*lipoprotein\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'
                ],
                'unit': 'mg/dL',
                'normal_range': '>40',
                'normal_min': 40,
                'normal_max': 999
            },
            'triglycerides': {
                'patterns': [
                    r'triglycerides\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'tg\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'trigs\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'
                ],
                'unit': 'mg/dL',
                'normal_range': '<150',
                'normal_min': 0,
                'normal_max': 150
            },
            'wbc': {
                'patterns': [
                    r'wbc\s*:?\s*(\d+\.?\d*)\s*(\/μl|/ul|cells/μl)',
                    r'white\s*blood\s*cells\s*:?\s*(\d+\.?\d*)\s*(\/μl|/ul|cells/μl)',
                    r'leukocytes\s*:?\s*(\d+\.?\d*)\s*(\/μl|/ul|cells/μl)'
                ],
                'unit': '/μL',
                'normal_range': '4000-11000',
                'normal_min': 4000,
                'normal_max': 11000
            },
            'platelets': {
                'patterns': [
                    r'platelets\s*:?\s*(\d+\.?\d*)\s*(\/μl|/ul|cells/μl)',
                    r'plt\s*:?\s*(\d+\.?\d*)\s*(\/μl|/ul|cells/μl)',
                    r'thrombocytes\s*:?\s*(\d+\.?\d*)\s*(\/μl|/ul|cells/μl)'
                ],
                'unit': '/μL',
                'normal_range': '150000-450000',
                'normal_min': 150000,
                'normal_max': 450000
            },
            'hematocrit': {
                'patterns': [
                    r'hematocrit\s*:?\s*(\d+\.?\d*)\s*%',
                    r'hct\s*:?\s*(\d+\.?\d*)\s*%',
                    r'packed\s*cell\s*volume\s*:?\s*(\d+\.?\d*)\s*%'
                ],
                'unit': '%',
                'normal_range': '36-46',
                'normal_min': 36,
                'normal_max': 46
            },
            # Liver Function Tests
            'alt': {
                'patterns': [
                    r'alt\s*:?\s*(\d+\.?\d*)\s*(u/l|iu/l)',
                    r'alanine\s*aminotransferase\s*:?\s*(\d+\.?\d*)\s*(u/l|iu/l)',
                    r'sgpt\s*:?\s*(\d+\.?\d*)\s*(u/l|iu/l)'
                ],
                'unit': 'U/L',
                'normal_range': '7-45',
                'normal_min': 7,
                'normal_max': 45
            },
            'ast': {
                'patterns': [
                    r'ast\s*:?\s*(\d+\.?\d*)\s*(u/l|iu/l)',
                    r'aspartate\s*aminotransferase\s*:?\s*(\d+\.?\d*)\s*(u/l|iu/l)',
                    r'sgot\s*:?\s*(\d+\.?\d*)\s*(u/l|iu/l)'
                ],
                'unit': 'U/L',
                'normal_range': '8-40',
                'normal_min': 8,
                'normal_max': 40
            },
            'bilirubin_total': {
                'patterns': [
                    r'total\s*bilirubin\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'bilirubin\s*total\s*:?\s*(\d+\.?\d*)\s*(mg/dl)',
                    r'bil\s*total\s*:?\s*(\d+\.?\d*)\s*(mg/dl)'
                ],
                'unit': 'mg/dL',
                'normal_range': '0.3-1.2',
                'normal_min': 0.3,
                'normal_max': 1.2
            },
            'albumin': {
                'patterns': [
                    r'albumin\s*:?\s*(\d+\.?\d*)\s*(g/dl)',
                    r'alb\s*:?\s*(\d+\.?\d*)\s*(g/dl)'
                ],
                'unit': 'g/dL',
                'normal_range': '3.5-5.0',
                'normal_min': 3.5,
                'normal_max': 5.0
            },
            # Blood Pressure (if mentioned in text)
            'blood_pressure': {
                'patterns': [
                    r'bp\s*:?\s*(\d+)\/(\d+)\s*(mmhg)?',
                    r'blood\s*pressure\s*:?\s*(\d+)\/(\d+)\s*(mmhg)?'
                ],
                'unit': 'mmHg',
                'normal_range': '120/80',
                'normal_systolic_max': 120,
                'normal_diastolic_max': 80
            }
        }
    
    def _load_facility_patterns(self) -> List[str]:
        """Load patterns to identify medical facilities"""
        return [
            r'(.*?(?:hospital|clinic|medical center|diagnostics|lab|laboratory|healthcare|pathology).*?)(?:\n|$)',
            r'(.*?(?:dr\.|doctor|physician).*?)(?:\n|$)',
            r'report\s*from\s*:?\s*(.*?)(?:\n|$)',
            r'issued\s*by\s*:?\s*(.*?)(?:\n|$)'
        ]
    
    def _load_date_patterns(self) -> List[str]:
        """Load patterns to identify test dates"""
        return [
            r'date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'test\s*date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'collected\s*on\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})',
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{2,4})'
        ]
    
    def _load_test_type_patterns(self) -> Dict[str, List[str]]:
        """Load patterns to identify test types"""
        return {
            'Blood Test': [
                r'complete\s*blood\s*count',
                r'cbc',
                r'blood\s*test',
                r'hematology',
                r'hemogram'
            ],
            'Lipid Panel': [
                r'lipid\s*profile',
                r'lipid\s*panel',
                r'cholesterol\s*test',
                r'lipogram'
            ],
            'Liver Function Test': [
                r'liver\s*function\s*test',
                r'lft',
                r'hepatic\s*panel',
                r'liver\s*profile'
            ],
            'Kidney Function Test': [
                r'kidney\s*function\s*test',
                r'kft',
                r'renal\s*function',
                r'creatinine',
                r'urea'
            ],
            'Thyroid Function Test': [
                r'thyroid\s*function\s*test',
                r'tft',
                r'thyroid\s*profile',
                r'tsh',
                r't3',
                r't4'
            ]
        }
    
    async def extract_biomarkers(self, text: str) -> Dict[str, Any]:
        """Extract biomarkers and medical information from text"""
        try:
            if not text:
                return self._empty_result()
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(text)
            
            # Extract different components
            biomarkers = self._extract_biomarker_values(cleaned_text)
            test_type = self._extract_test_type(cleaned_text)
            facility = self._extract_facility(cleaned_text)
            test_date = self._extract_date(cleaned_text)
            entities = self._extract_named_entities(cleaned_text) if self.nlp else []
            
            logger.info(f"Extracted {len(biomarkers)} biomarkers from text")
            
            return {
                'biomarkers': biomarkers,
                'test_type': test_type,
                'facility': facility,
                'date': test_date,
                'entities': entities,
                'confidence_score': self._calculate_confidence(biomarkers, text),
                'text_length': len(text),
                'processed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting biomarkers: {e}")
            return self._empty_result()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better processing"""
        # Convert to lowercase for pattern matching
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Replace common OCR errors
        replacements = {
            'o': '0',  # Common OCR confusion
            'i': '1',  # In numeric contexts
            'l': '1',  # In numeric contexts
            'mg%': 'mg/dl',
            'gm%': 'g/dl',
            'gm/dl': 'g/dl'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _extract_biomarker_values(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Extract biomarker values using regex patterns"""
        biomarkers = {}
        
        for biomarker_name, config in self.biomarker_patterns.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        if biomarker_name == 'blood_pressure':
                            # Special handling for blood pressure
                            systolic = float(match.group(1))
                            diastolic = float(match.group(2))
                            
                            status = self._determine_bp_status(
                                systolic, diastolic, 
                                config['normal_systolic_max'],
                                config['normal_diastolic_max']
                            )
                            
                            biomarkers[biomarker_name] = {
                                'systolic': systolic,
                                'diastolic': diastolic,
                                'unit': config['unit'],
                                'range': config['normal_range'],
                                'status': status
                            }
                        else:
                            # Standard biomarker handling
                            value = float(match.group(1))
                            unit = match.group(2) if len(match.groups()) > 1 else config['unit']
                            
                            status = self._determine_status(
                                value, 
                                config.get('normal_min', 0),
                                config.get('normal_max', float('inf'))
                            )
                            
                            biomarkers[biomarker_name] = {
                                'value': value,
                                'unit': unit,
                                'range': config['normal_range'],
                                'status': status
                            }
                        
                        break  # Use first match found
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing {biomarker_name}: {e}")
                        continue
        
        return biomarkers
    
    def _determine_status(self, value: float, min_normal: float, max_normal: float) -> str:
        """Determine if a biomarker value is normal, borderline, or abnormal"""
        if min_normal <= value <= max_normal:
            return 'normal'
        elif (min_normal * 0.9) <= value <= (max_normal * 1.1):
            return 'borderline'
        else:
            return 'abnormal'
    
    def _determine_bp_status(self, systolic: float, diastolic: float, 
                            normal_systolic: float, normal_diastolic: float) -> str:
        """Determine blood pressure status"""
        if systolic <= normal_systolic and diastolic <= normal_diastolic:
            return 'normal'
        elif systolic <= normal_systolic * 1.1 and diastolic <= normal_diastolic * 1.1:
            return 'borderline'
        else:
            return 'abnormal'
    
    def _extract_test_type(self, text: str) -> str:
        """Extract test type from text"""
        for test_type, patterns in self.test_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return test_type
        
        # Default inference based on biomarkers found
        text_lower = text.lower()
        if any(term in text_lower for term in ['cholesterol', 'ldl', 'hdl', 'triglycerides']):
            return 'Lipid Panel'
        elif any(term in text_lower for term in ['alt', 'ast', 'bilirubin', 'albumin']):
            return 'Liver Function Test'
        elif any(term in text_lower for term in ['hemoglobin', 'wbc', 'platelets', 'hematocrit']):
            return 'Complete Blood Count'
        else:
            return 'Medical Test'
    
    def _extract_facility(self, text: str) -> str:
        """Extract medical facility name from text"""
        for pattern in self.facility_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                facility = match.group(1).strip()
                if len(facility) > 5 and len(facility) < 100:  # Reasonable length
                    return facility
        
        return 'Medical Facility'
    
    def _extract_date(self, text: str) -> str:
        """Extract test date from text"""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    # Try to parse and standardize the date
                    parsed_date = self._parse_date(date_str)
                    return parsed_date
                except:
                    continue
        
        # Default to current date if no date found
        return datetime.now().strftime('%Y-%m-%d')
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats and return standardized format"""
        date_str = date_str.strip()
        
        # Common date formats
        formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y',
            '%d/%m/%y', '%d-%m-%y', '%m/%d/%y', '%m-%d-%y',
            '%Y/%m/%d', '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # If no format matches, return current date
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_named_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'DATE', 'CARDINAL', 'QUANTITY']:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'confidence': 0.8  # spaCy doesn't provide confidence scores
                    })
            
            return entities
        except Exception as e:
            logger.warning(f"Error extracting named entities: {e}")
            return []
    
    def _calculate_confidence(self, biomarkers: Dict, text: str) -> float:
        """Calculate overall confidence score for the extraction"""
        if not biomarkers:
            return 0.0
        
        # Base confidence on number of biomarkers found and text quality
        biomarker_score = min(len(biomarkers) * 0.2, 1.0)
        
        # Text quality indicators
        text_length_score = min(len(text) / 1000, 1.0)
        
        # Check for medical keywords
        medical_keywords = [
            'test', 'result', 'normal', 'abnormal', 'range', 
            'laboratory', 'clinic', 'hospital', 'doctor', 'patient'
        ]
        keyword_score = sum(1 for keyword in medical_keywords if keyword in text.lower()) / len(medical_keywords)
        
        # Weighted average
        confidence = (biomarker_score * 0.5 + text_length_score * 0.2 + keyword_score * 0.3)
        
        return round(min(confidence, 1.0), 2)
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'biomarkers': {},
            'test_type': 'Unknown',
            'facility': 'Unknown Facility',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'entities': [],
            'confidence_score': 0.0,
            'text_length': 0,
            'processed_at': datetime.utcnow().isoformat()
        }
    
    async def validate_biomarker_data(self, biomarkers: Dict[str, Dict]) -> Dict[str, Any]:
        """Validate extracted biomarker data"""
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        for biomarker_name, data in biomarkers.items():
            # Check if biomarker exists in our patterns
            if biomarker_name not in self.biomarker_patterns:
                validation_results['warnings'].append(f"Unknown biomarker: {biomarker_name}")
                continue
            
            # Validate value ranges
            if 'value' in data:
                value = data['value']
                config = self.biomarker_patterns[biomarker_name]
                
                # Check for extremely abnormal values
                if 'normal_max' in config and value > config['normal_max'] * 5:
                    validation_results['warnings'].append(
                        f"{biomarker_name} value {value} seems extremely high"
                    )
                
                # Suggest retesting for borderline values
                if data.get('status') == 'borderline':
                    validation_results['suggestions'].append(
                        f"Consider retesting {biomarker_name} as value is borderline"
                    )
        
        return validation_results
