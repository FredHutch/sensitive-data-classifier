"""
HIPAA Identifier Detection System

Comprehensive detection system for all 18 HIPAA identifier types
as defined in the HIPAA Privacy Rule.
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class HIPAAIdentifier:
    """
    Enhanced HIPAA identifier detection system covering all 18 identifier types
    """
    
    def __init__(self):
        self.identifier_patterns = self._create_comprehensive_patterns()
        self.medical_keywords = self._load_medical_keywords()
        logger.info("HIPAA Identifier system initialized")
    
    def _create_comprehensive_patterns(self) -> Dict[str, List[str]]:
        """
        Create comprehensive regex patterns for all 18 HIPAA identifiers
        """
        patterns = {
            'names': [
                r'\b(?:Mr|Mrs|Ms|Dr|Doctor|Patient|Subject)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
                r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b',
                r'\b[A-Z]\.\s*[A-Z][a-z]+\b',
                r'\b[A-Z][a-z]+\s+[A-Z]\.\b',
                r'(?i)(?:name|patient|individual):\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*'
            ],
            'addresses': [
                r'\d+\s+[A-Z][a-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct|Place|Pl|Circle|Cir)\b',
                r'\b[A-Z][a-z]+,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?\b',
                r'\b\d{5}(?:-\d{4})?\b',
                r'\b\d+\s+[A-Z][a-z\s]+(?:Apt|Unit|Suite|Ste|#)\s*\d+[A-Z]?\b',
                r'(?i)(?:address|residence|home):\s*\d+\s+[A-Za-z\s,]+\d{5}'
            ],
            'dates': [
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
                r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}\b',
                r'(?i)(?:dob|birth|born|admitted|discharged|died|deceased|visit|appointment)(?:\s+date)?:?\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'(?i)age\s*:?\s*(?:8[9]|9[0-9]|\d{3,})\b'
            ],
            'phone_numbers': [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',
                r'(?i)(?:phone|tel|telephone|cell|mobile|contact):?\s*\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}',
                r'\b1[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            ],
            'fax_numbers': [
                r'(?i)fax:?\s*\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}',
                r'(?i)f:\s*\d{3}[-.]?\d{3}[-.]?\d{4}'
            ],
            'email_addresses': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                r'(?i)(?:email|e-mail):?\s*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
            ],
            'ssn': [
                r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
                r'(?i)(?:ssn|social\s*security|ss#):?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}'
            ],
            'medical_record_numbers': [
                r'(?i)(?:mrn|medical\s*record|record\s*number|chart\s*number|patient\s*id):?\s*[A-Z0-9-]{4,15}',
                r'\bMR\d{4,12}\b',
                r'\b(?:MRN|PT|PAT)\d{4,12}\b'
            ],
            'health_plan_numbers': [
                r'(?i)(?:insurance|policy|member|subscriber|medicaid|medicare|plan):?\s*(?:number|id|#):?\s*[A-Z0-9-]{6,20}',
                r'(?i)group\s*number:?\s*[A-Z0-9-]{6,15}'
            ],
            'account_numbers': [
                r'(?i)(?:account|acct|bill|invoice):?\s*(?:number|#):?\s*[A-Z0-9-]{6,20}',
                r'(?i)(?:financial|payment)\s*(?:account|id):?\s*[A-Z0-9-]{6,20}'
            ],
            'certificate_numbers': [
                r'(?i)(?:license|certificate|cert|permit):?\s*(?:number|#):?\s*[A-Z0-9-]{4,15}',
                r'(?i)(?:driver|medical|professional)\s*license:?\s*[A-Z0-9-]{4,15}'
            ],
            'vehicle_identifiers': [
                r'\b[A-Z]{1,3}[-\s]?\d{1,4}[-\s]?[A-Z0-9]{0,3}\b',
                r'\bVIN:?\s*[A-HJ-NPR-Z0-9]{17}\b',
                r'(?i)(?:license\s*plate|plate\s*number):?\s*[A-Z0-9-\s]{3,10}'
            ],
            'device_identifiers': [
                r'(?i)(?:device|serial|model):?\s*(?:number|id|#):?\s*[A-Z0-9-]{6,25}',
                r'(?i)(?:pacemaker|implant|prosthetic):?\s*(?:id|serial):?\s*[A-Z0-9-]{6,25}',
                r'(?i)(?:equipment|instrument)\s*(?:id|serial):?\s*[A-Z0-9-]{6,25}'
            ],
            'urls': [
                r'https?://[^\s<>"\'’]+',
                r'www\.[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
                r'\b[a-zA-Z0-9.-]+\.(?:com|org|net|edu|gov|mil|info|biz)\b'
            ],
            'ip_addresses': [
                r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
                r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
            ],
            'biometric_identifiers': [
                r'(?i)(?:fingerprint|voiceprint|retinal|iris|biometric):?\s*(?:scan|print|id):?\s*[A-Z0-9-]{8,30}',
                r'(?i)(?:facial|voice|palm)\s*(?:recognition|scan|print):?\s*[A-Z0-9-]{8,30}'
            ],
            'photo_images': [
                r'(?i)(?:photo|image|picture|photograph):?\s*[A-Za-z0-9_-]+\.(?:jpg|jpeg|png|gif|bmp|tiff)',
                r'(?i)(?:photograph|image)\s*(?:of|showing|depicting)\s*(?:patient|individual|face|person)'
            ],
            'other_identifiers': [
                r'(?i)(?:employee|patient|customer|client):?\s*(?:id|number|#):?\s*[A-Z0-9-]{4,20}',
                r'(?i)(?:badge|id\s*card|access\s*card):?\s*(?:number):?\s*[A-Z0-9-]{4,20}',
                r'(?i)(?:reference|case|ticket)\s*(?:number|id):?\s*[A-Z0-9-]{4,20}'
            ]
        }
        return patterns
    
    def _load_medical_keywords(self) -> List[str]:
        """
        Load comprehensive medical keywords for context analysis
        """
        return [
            'patient', 'doctor', 'physician', 'nurse', 'hospital', 'clinic', 'medical',
            'diagnosis', 'treatment', 'prescription', 'medication', 'medicine', 'drug',
            'surgery', 'operation', 'procedure', 'therapy', 'rehabilitation', 'recovery',
            'examination', 'exam', 'test', 'lab', 'laboratory', 'result', 'report',
            'record', 'chart', 'file', 'document', 'history', 'medical history',
            'admission', 'discharge', 'emergency', 'urgent', 'care', 'healthcare',
            'health', 'wellness', 'condition', 'disease', 'illness', 'disorder',
            'symptom', 'sign', 'complaint', 'problem', 'issue', 'concern',
            'blood', 'urine', 'specimen', 'sample', 'biopsy', 'culture',
            'x-ray', 'mri', 'ct scan', 'ultrasound', 'ekg', 'ecg', 'imaging',
            'vital signs', 'temperature', 'pulse', 'pressure', 'respiratory',
            'allergies', 'medications', 'immunizations', 'vaccines', 'shots'
        ]
    
    def identify_phi_elements(self, text: str) -> Dict[str, List[str]]:
        """
        Identify all PHI elements in the given text
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict[str, List[str]]: Dictionary of PHI categories and found elements
        """
        found_phi = {}
        
        for category, patterns in self.identifier_patterns.items():
            matches = set()
            for pattern in patterns:
                try:
                    found = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if found and isinstance(found[0], tuple):
                        # Handle grouped matches
                        found = [match[0] if isinstance(match, tuple) else match for match in found]
                    matches.update(found)
                except Exception as e:
                    logger.warning(f"Pattern matching error in {category}: {e}")
                    continue
            
            if matches:
                # Filter out very short matches that are likely false positives
                filtered_matches = [match.strip() for match in matches 
                                 if len(match.strip()) >= 2]
                if filtered_matches:
                    found_phi[category] = filtered_matches
                
        return found_phi
    
    def calculate_phi_score(self, text: str) -> float:
        """
        Calculate comprehensive PHI score (0-1) based on identifiers found
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            float: PHI score between 0 and 1
        """
        phi_elements = self.identify_phi_elements(text)
        
        if not phi_elements:
            return 0.0
        
        # Enhanced weights based on HIPAA risk levels
        weights = {
            'names': 0.18,
            'addresses': 0.15,
            'dates': 0.08,
            'phone_numbers': 0.12,
            'fax_numbers': 0.10,
            'email_addresses': 0.12,
            'ssn': 0.25,  # Highest weight for SSN
            'medical_record_numbers': 0.20,
            'health_plan_numbers': 0.18,
            'account_numbers': 0.10,
            'certificate_numbers': 0.10,
            'vehicle_identifiers': 0.08,
            'device_identifiers': 0.12,
            'urls': 0.06,
            'ip_addresses': 0.08,
            'biometric_identifiers': 0.22,
            'photo_images': 0.15,
            'other_identifiers': 0.10
        }
        
        total_score = 0.0
        for category, items in phi_elements.items():
            weight = weights.get(category, 0.05)
            # Score with diminishing returns but higher base value
            item_count = len(set(items))  # Use unique items only
            category_score = min(1.0, (item_count * weight * 0.7) + (weight * 0.3))
            total_score += category_score
        
        # Apply medical context multiplier
        medical_keywords_found = sum(1 for keyword in self.medical_keywords 
                                   if keyword.lower() in text.lower())
        if medical_keywords_found > 3:
            total_score *= 1.2  # Increase score for medical context
        
        return min(1.0, total_score)
    
    def get_risk_assessment(self, phi_score: float, phi_elements: Dict[str, List[str]]) -> str:
        """
        Assess risk level based on PHI score and elements found
        
        Args:
            phi_score (float): Calculated PHI score
            phi_elements (Dict): Dictionary of found PHI elements
            
        Returns:
            str: Risk level (HIGH/MEDIUM/LOW/NONE)
        """
        if phi_score == 0:
            return 'NONE'
        
        high_risk_categories = {'ssn', 'medical_record_numbers', 'biometric_identifiers'}
        has_high_risk = any(cat in phi_elements for cat in high_risk_categories)
        
        if has_high_risk or phi_score > 0.8:
            return 'HIGH'
        elif phi_score > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
