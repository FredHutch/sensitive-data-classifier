"""
Clinical Coherence Module

Provides clinically appropriate mappings between diagnoses, medications, and lab values
to ensure synthetic data generation is realistic and representative.
"""

import random
from typing import List, Dict, Any, Tuple

class ClinicalCoherenceEngine:
    """
    Ensures clinical coherence in synthetic health data by providing
    appropriate correlations between diagnoses, medications, lab values, and demographics.
    """

    def __init__(self):
        self.diagnosis_medication_map = self._initialize_diagnosis_medication_map()
        self.diagnosis_lab_abnormalities = self._initialize_diagnosis_lab_map()
        self.age_diagnosis_correlations = self._initialize_age_diagnosis_map()
        self.gender_specific_diagnoses = self._initialize_gender_diagnoses()

    def _initialize_diagnosis_medication_map(self) -> Dict[str, List[str]]:
        """
        Map diagnoses to clinically appropriate medication categories
        """
        return {
            # Cardiovascular
            'Essential hypertension': ['ace_inhibitors', 'arbs', 'beta_blockers', 'calcium_channel_blockers'],
            'ST-elevation myocardial infarction': ['beta_blockers', 'ace_inhibitors', 'statins', 'analgesics'],
            'Heart failure': ['ace_inhibitors', 'beta_blockers', 'arbs'],
            'Atrial fibrillation': ['beta_blockers', 'calcium_channel_blockers'],

            # Endocrine
            'Type 2 diabetes mellitus': ['diabetes_medications'],
            'Type 1 diabetes mellitus': ['diabetes_medications'],
            'Hypothyroidism': [],  # Would need thyroid medications

            # Respiratory
            'Asthma': [],  # Would need bronchodilators
            'Chronic obstructive pulmonary disease': [],
            'Pneumonia': ['antibiotics'],
            'Acute bronchitis': ['antibiotics'],

            # Infectious
            'Streptococcal sepsis': ['antibiotics'],
            'Staphylococcal infection': ['antibiotics'],
            'Pneumococcal pneumonia': ['antibiotics'],
            'Influenza': [],

            # Pain management
            'Arthritis': ['analgesics'],
            'Osteoporosis': [],
            'Back pain': ['analgesics'],
            'Joint pain': ['analgesics'],

            # Mental health
            'Major depressive disorder': [],
            'Generalized anxiety disorder': [],
            'Bipolar I disorder': [],

            # Gastrointestinal
            'Gastroesophageal reflux disease': [],
            'Peptic ulcer disease': [],
            'Inflammatory bowel disease': [],

            # Neoplasms
            'Lung adenocarcinoma': ['analgesics'],
            'Invasive ductal carcinoma of breast': ['analgesics'],
            'Colorectal adenocarcinoma': ['analgesics'],
            'Prostate adenocarcinoma': ['analgesics'],
        }

    def _initialize_diagnosis_lab_map(self) -> Dict[str, Dict[str, str]]:
        """
        Map diagnoses to expected lab abnormalities
        """
        return {
            'Type 2 diabetes mellitus': {
                'Glucose': 'high',
                'Hemoglobin A1c': 'high'
            },
            'Type 1 diabetes mellitus': {
                'Glucose': 'high',
                'Hemoglobin A1c': 'high'
            },
            'Iron deficiency anemia': {
                'Hemoglobin': 'low',
                'Hematocrit': 'low',
                'Mean Corpuscular Volume': 'low'
            },
            'Sickle cell anemia': {
                'Hemoglobin': 'low',
                'Hematocrit': 'low'
            },
            'Chronic hepatitis C': {
                'ALT (Alanine Aminotransferase)': 'high',
                'AST (Aspartate Aminotransferase)': 'high',
                'Total Bilirubin': 'high'
            },
            'Alcoholic liver disease': {
                'ALT (Alanine Aminotransferase)': 'high',
                'AST (Aspartate Aminotransferase)': 'high',
                'Total Bilirubin': 'high'
            },
            'ST-elevation myocardial infarction': {
                'Troponin I': 'critical',
                'Troponin T': 'critical',
                'CK-MB': 'high'
            },
            'Non-ST elevation myocardial infarction': {
                'Troponin I': 'critical',
                'CK-MB': 'high'
            },
            'Heart failure': {
                'B-type Natriuretic Peptide': 'high'
            },
            'Hypothyroidism': {
                'TSH (Thyroid Stimulating Hormone)': 'high',
                'Free T4': 'low'
            },
            'Hyperthyroidism': {
                'TSH (Thyroid Stimulating Hormone)': 'low',
                'Free T4': 'high'
            },
            'Essential hypertension': {
                # Often no specific lab abnormalities
            },
            'Deep vein thrombosis': {
                'Partial Thromboplastin Time': 'high'
            }
        }

    def _initialize_age_diagnosis_map(self) -> Dict[str, Tuple[int, int]]:
        """
        Map diagnoses to typical age ranges
        """
        return {
            # Pediatric/Young adult
            'Asthma': (5, 40),
            'Type 1 diabetes mellitus': (5, 30),
            'Autism': (3, 10),

            # Middle age
            'Type 2 diabetes mellitus': (40, 80),
            'Essential hypertension': (35, 85),
            'Major depressive disorder': (20, 70),
            'Generalized anxiety disorder': (20, 60),

            # Elderly
            'Alzheimer disease': (65, 95),
            'Parkinson disease': (60, 90),
            'Osteoporosis': (60, 95),
            'Prostate adenocarcinoma': (55, 85),
            'Atrial fibrillation': (60, 90),
            'ST-elevation myocardial infarction': (50, 85),
            'Heart failure': (60, 90),

            # All ages
            'Pneumonia': (0, 95),
            'Influenza': (0, 95),
            'Gastroesophageal reflux disease': (20, 80),
        }

    def _initialize_gender_diagnoses(self) -> Dict[str, List[str]]:
        """
        Gender-specific diagnoses
        """
        return {
            'Male': [
                'Prostate adenocarcinoma',
                'Benign prostatic hyperplasia',
                'Prostatectomy'
            ],
            'Female': [
                'Invasive ductal carcinoma of breast',
                'Uterine fibroid',
                'Gestational diabetes',
                'Pregnancy complications',
                'Mastectomy',
                'Hysterectomy',
                'Cesarean section',
                'Ovarian cyst'
            ]
        }

    def get_appropriate_medications(self, diagnosis: str, num_medications: int = None) -> List[str]:
        """
        Get clinically appropriate medication categories for a diagnosis

        Args:
            diagnosis: Primary diagnosis name
            num_medications: Number of medications to return (None for all appropriate)

        Returns:
            List of medication category names
        """
        # Get mapped medication categories
        med_categories = self.diagnosis_medication_map.get(diagnosis, [])

        # If no specific mapping, return common categories
        if not med_categories:
            med_categories = ['analgesics']  # Pain relief is common

        # Add common comorbidity medications
        # Many patients have multiple conditions
        if random.random() < 0.3:  # 30% chance of hypertension comorbidity
            if 'ace_inhibitors' not in med_categories:
                med_categories.append(random.choice(['ace_inhibitors', 'beta_blockers']))

        if random.random() < 0.2:  # 20% chance of hyperlipidemia
            if 'statins' not in med_categories:
                med_categories.append('statins')

        # Return requested number or all
        if num_medications and len(med_categories) > num_medications:
            return random.sample(med_categories, num_medications)

        return med_categories

    def adjust_lab_values_for_diagnosis(
        self,
        diagnosis: str,
        lab_results: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Adjust lab values to be consistent with diagnosis

        Args:
            diagnosis: Primary diagnosis
            lab_results: Generated lab results

        Returns:
            Adjusted lab results
        """
        expected_abnormalities = self.diagnosis_lab_abnormalities.get(diagnosis, {})

        for test_name, abnormality_type in expected_abnormalities.items():
            if test_name in lab_results:
                # Adjust value based on abnormality type
                current_value = lab_results[test_name]

                # Extract numeric value
                import re
                match = re.search(r'([0-9.]+)', current_value)
                if match:
                    value = float(match.group(1))
                    unit = current_value.replace(match.group(1), '').strip()

                    # Adjust based on type
                    if abnormality_type == 'high':
                        adjusted_value = value * random.uniform(1.3, 2.0)
                    elif abnormality_type == 'low':
                        adjusted_value = value * random.uniform(0.3, 0.7)
                    elif abnormality_type == 'critical':
                        adjusted_value = value * random.uniform(5.0, 20.0)
                    else:
                        adjusted_value = value

                    lab_results[test_name] = f"{adjusted_value:.1f} {unit}"

        return lab_results

    def is_diagnosis_appropriate_for_demographics(
        self,
        diagnosis: str,
        age: int,
        gender: str
    ) -> bool:
        """
        Check if diagnosis is appropriate for patient demographics

        Args:
            diagnosis: Diagnosis name
            age: Patient age
            gender: Patient gender

        Returns:
            True if appropriate, False otherwise
        """
        # Check gender-specific diagnoses
        if gender == 'Male' and diagnosis in self.gender_specific_diagnoses.get('Female', []):
            return False
        if gender == 'Female' and diagnosis in self.gender_specific_diagnoses.get('Male', []):
            return False

        # Check age appropriateness
        if diagnosis in self.age_diagnosis_correlations:
            min_age, max_age = self.age_diagnosis_correlations[diagnosis]
            if not (min_age <= age <= max_age):
                # Allow some flexibility (10% of cases can be outside typical range)
                return random.random() < 0.1

        return True

    def get_appropriate_secondary_diagnoses(
        self,
        primary_diagnosis: str,
        age: int,
        num_secondary: int = 2
    ) -> List[str]:
        """
        Get clinically appropriate secondary diagnoses (comorbidities)

        Args:
            primary_diagnosis: Primary diagnosis
            age: Patient age
            num_secondary: Number of secondary diagnoses to generate

        Returns:
            List of secondary diagnosis names
        """
        common_comorbidities = {
            'Type 2 diabetes mellitus': [
                'Essential hypertension',
                'Hyperlipidemia',
                'Chronic kidney disease'
            ],
            'Heart failure': [
                'Essential hypertension',
                'Atrial fibrillation',
                'Type 2 diabetes mellitus',
                'Chronic kidney disease'
            ],
            'Chronic obstructive pulmonary disease': [
                'Essential hypertension',
                'Coronary artery disease',
                'Anxiety disorder'
            ],
            'ST-elevation myocardial infarction': [
                'Essential hypertension',
                'Type 2 diabetes mellitus',
                'Hyperlipidemia',
                'Tobacco use disorder'
            ]
        }

        # Get related comorbidities
        possible_secondary = common_comorbidities.get(primary_diagnosis, [])

        # Add age-related conditions
        if age > 60:
            possible_secondary.extend([
                'Essential hypertension',
                'Osteoarthritis',
                'Hyperlipidemia'
            ])

        # Remove duplicates and primary diagnosis
        possible_secondary = list(set(possible_secondary))
        if primary_diagnosis in possible_secondary:
            possible_secondary.remove(primary_diagnosis)

        # Return random sample
        if not possible_secondary:
            return []

        return random.sample(
            possible_secondary,
            min(num_secondary, len(possible_secondary))
        )
