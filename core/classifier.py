"""
Advanced PHI Classifier - Production Ready with Pre-trained Models

Uses state-of-the-art pre-trained models for PHI detection:
- Pre-trained NER models for entity recognition
- Pre-trained text classifiers for document-level classification
- Hybrid rule-based + ML approach for maximum accuracy

Models are downloaded automatically on first run and cached locally.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import time
import warnings
from pathlib import Path
import json
import re

warnings.filterwarnings('ignore')

# Core ML imports
from sklearn.preprocessing import StandardScaler

# Try to import transformers (required for production use)
try:
    from transformers import (
        AutoTokenizer,
        AutoModelForTokenClassification,
        AutoModelForSequenceClassification,
        pipeline
    )
    import torch
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Try to import spaCy (alternative NER approach)
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

from .hipaa_identifier import HIPAAIdentifier

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages downloading and caching of pre-trained models
    """

    def __init__(self, cache_dir: str = "./models_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.models = {}
        logger.info(f"Model cache directory: {self.cache_dir}")

    def get_ner_model(self):
        """
        Get pre-trained NER model for entity recognition.
        Uses BioBERT fine-tuned for biomedical NER.
        Falls back to lighter models if needed.
        """
        if "ner" in self.models:
            return self.models["ner"]

        if not HAS_TRANSFORMERS:
            logger.warning("Transformers library not available. NER disabled.")
            return None

        try:
            # Try to load BioBERT NER model (optimized for medical text)
            logger.info("Loading BioBERT NER model for medical entity recognition...")

            # Use a lightweight but effective model for NER
            # This model is fine-tuned on biomedical texts
            model_name = "d4data/biomedical-ner-all"

            ner_pipeline = pipeline(
                "ner",
                model=model_name,
                tokenizer=model_name,
                aggregation_strategy="simple",
                device=-1  # Use CPU (change to 0 for GPU)
            )

            self.models["ner"] = ner_pipeline
            logger.info(f"NER model loaded successfully: {model_name}")
            return ner_pipeline

        except Exception as e:
            logger.warning(f"Failed to load specialized NER model: {e}")

            try:
                # Fallback to general-purpose NER
                logger.info("Loading fallback NER model...")
                model_name = "dslim/bert-base-NER"

                ner_pipeline = pipeline(
                    "ner",
                    model=model_name,
                    tokenizer=model_name,
                    aggregation_strategy="simple",
                    device=-1
                )

                self.models["ner"] = ner_pipeline
                logger.info(f"Fallback NER model loaded: {model_name}")
                return ner_pipeline

            except Exception as e2:
                logger.error(f"Failed to load any NER model: {e2}")
                return None

    def get_text_classifier(self):
        """
        Get pre-trained text classification model.
        This is a zero-shot classifier that can identify PHI-containing documents.
        """
        if "classifier" in self.models:
            return self.models["classifier"]

        if not HAS_TRANSFORMERS:
            logger.warning("Transformers library not available. Text classification disabled.")
            return None

        try:
            # Use zero-shot classification for PHI detection
            # This allows classification without task-specific training
            logger.info("Loading zero-shot classification model...")

            classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # CPU
            )

            self.models["classifier"] = classifier
            logger.info("Text classifier loaded successfully")
            return classifier

        except Exception as e:
            logger.error(f"Failed to load text classifier: {e}")
            return None

    def get_clinical_bert_embeddings(self):
        """
        Get ClinicalBERT for medical text embeddings.
        Smaller model suitable for moderate compute.
        """
        if "embeddings" in self.models:
            return self.models["embeddings"]

        if not HAS_TRANSFORMERS:
            logger.warning("Transformers library not available. Embeddings disabled.")
            return None

        try:
            # Use a smaller, efficient model for embeddings
            logger.info("Loading clinical text embedding model...")

            model_name = "emilyalsentzer/Bio_ClinicalBERT"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=2,
                problem_type="single_label_classification"
            )

            # Put in eval mode
            model.eval()

            self.models["embeddings"] = {
                "tokenizer": tokenizer,
                "model": model
            }

            logger.info("Clinical embeddings model loaded successfully")
            return self.models["embeddings"]

        except Exception as e:
            logger.warning(f"Failed to load clinical embeddings: {e}")
            return None


class AdvancedPHIClassifier:
    """
    Production-ready PHI classifier using pre-trained models.

    Features:
    - Pre-trained NER for entity recognition
    - Zero-shot classification for document-level PHI detection
    - Hybrid rule-based + ML approach
    - Automatic model downloading and caching
    - Works with moderate compute (CPU-friendly)
    """

    def __init__(self, cache_dir: str = "./models_cache"):
        self.hipaa_identifier = HIPAAIdentifier()
        self.model_manager = ModelManager(cache_dir=cache_dir)

        # Load pre-trained models
        logger.info("Initializing PHI Classifier with pre-trained models...")
        self.ner_model = self.model_manager.get_ner_model()
        self.text_classifier = self.model_manager.get_text_classifier()
        self.embeddings_model = self.model_manager.get_clinical_bert_embeddings()

        # Medical context keywords for enhanced detection
        self.medical_keywords = self._load_medical_keywords()

        # PHI candidate labels for zero-shot classification
        self.phi_labels = [
            "medical record with patient information",
            "document containing protected health information",
            "clinical document with sensitive patient data",
            "personal health information document",
            "generic document without medical information"
        ]

        self.is_trained = True  # Pre-trained models are ready to use
        logger.info("PHI Classifier initialized successfully")
        logger.info(f"  - NER available: {self.ner_model is not None}")
        logger.info(f"  - Text classifier available: {self.text_classifier is not None}")
        logger.info(f"  - Clinical embeddings available: {self.embeddings_model is not None}")

    def _load_medical_keywords(self) -> List[str]:
        """Load comprehensive medical keywords"""
        return [
            'patient', 'medical', 'diagnosis', 'treatment', 'medication',
            'hospital', 'physician', 'doctor', 'nurse', 'clinical',
            'prescription', 'surgery', 'procedure', 'laboratory', 'test',
            'admission', 'discharge', 'emergency', 'vital signs', 'blood',
            'condition', 'disease', 'symptom', 'therapy', 'examination'
        ]

    def _extract_entities_with_ner(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities using pre-trained NER model
        """
        if not self.ner_model:
            return []

        try:
            # Run NER inference
            entities = self.ner_model(text)

            # Filter and format results
            phi_entities = []
            for entity in entities:
                # Focus on person names, locations, organizations, dates
                if entity['entity_group'] in ['PER', 'LOC', 'ORG', 'DATE', 'PERSON', 'GPE', 'DISEASE', 'CHEMICAL']:
                    phi_entities.append({
                        'text': entity['word'],
                        'type': entity['entity_group'],
                        'score': entity['score'],
                        'start': entity.get('start', 0),
                        'end': entity.get('end', 0)
                    })

            return phi_entities

        except Exception as e:
            logger.error(f"NER extraction error: {e}")
            return []

    def _classify_document_with_zeroshot(self, text: str) -> Tuple[bool, float]:
        """
        Classify document using zero-shot classification
        """
        if not self.text_classifier:
            # Fallback to rule-based
            return None, 0.0

        try:
            # Truncate text if too long (BART has 1024 token limit)
            max_chars = 2000
            text_sample = text[:max_chars] if len(text) > max_chars else text

            # Run zero-shot classification
            result = self.text_classifier(
                text_sample,
                candidate_labels=self.phi_labels,
                multi_label=False
            )

            # Check if top prediction is PHI-related
            top_label = result['labels'][0]
            top_score = result['scores'][0]

            # PHI if any of the first 4 labels (which are PHI-related)
            is_phi = top_label in self.phi_labels[:4]
            confidence = top_score if is_phi else (1.0 - top_score)

            return is_phi, float(confidence)

        except Exception as e:
            logger.error(f"Zero-shot classification error: {e}")
            return None, 0.0

    def _calculate_medical_context_score(self, text: str) -> float:
        """
        Calculate medical context score based on keyword presence
        """
        text_lower = text.lower()
        words = text_lower.split()

        if len(words) == 0:
            return 0.0

        # Count medical keyword matches
        medical_matches = sum(1 for keyword in self.medical_keywords if keyword in text_lower)

        # Normalize by text length with diminishing returns
        score = min(1.0, medical_matches / 10.0)

        return score

    def classify_document(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive document classification using pre-trained models.

        Combines:
        1. Rule-based HIPAA identifier detection
        2. NER-based entity recognition
        3. Zero-shot text classification
        4. Medical context analysis

        Args:
            text (str): Document text to classify

        Returns:
            Dict[str, Any]: Complete classification results
        """
        start_time = time.time()

        try:
            # 1. Rule-based HIPAA identifier detection
            phi_elements = self.hipaa_identifier.identify_phi_elements(text)
            phi_score = self.hipaa_identifier.calculate_phi_score(text)
            risk_level = self.hipaa_identifier.get_risk_assessment(phi_score, phi_elements)

            # 2. NER-based entity extraction
            ner_entities = self._extract_entities_with_ner(text)
            ner_score = min(1.0, len(ner_entities) / 10.0) if ner_entities else 0.0

            # 3. Zero-shot classification
            zeroshot_prediction, zeroshot_confidence = self._classify_document_with_zeroshot(text)

            # 4. Medical context analysis
            medical_context_score = self._calculate_medical_context_score(text)

            # 5. Ensemble decision
            if zeroshot_prediction is not None:
                # Use ML prediction as primary
                contains_phi = zeroshot_prediction
                confidence = zeroshot_confidence

                # Boost confidence if rule-based methods agree
                if phi_score > 0.3 and contains_phi:
                    confidence = min(1.0, confidence * 1.2)

                # Lower confidence if methods disagree
                if phi_score < 0.1 and contains_phi:
                    confidence = confidence * 0.8

            else:
                # Fallback to rule-based
                contains_phi = phi_score > 0.15 or ner_score > 0.3
                confidence = max(phi_score, ner_score)

            processing_time = time.time() - start_time

            return {
                'contains_phi': bool(contains_phi),
                'confidence': float(confidence),
                'phi_score': float(phi_score),
                'ner_score': float(ner_score),
                'medical_context_score': float(medical_context_score),
                'zeroshot_prediction': zeroshot_prediction,
                'zeroshot_confidence': float(zeroshot_confidence) if zeroshot_confidence else 0.0,
                'phi_elements_found': phi_elements,
                'ner_entities': ner_entities,
                'total_phi_identifiers': sum(len(items) for items in phi_elements.values()),
                'phi_categories': list(phi_elements.keys()),
                'risk_level': risk_level,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat(),
                'model_status': {
                    'ner_active': self.ner_model is not None,
                    'classifier_active': self.text_classifier is not None,
                    'embeddings_active': self.embeddings_model is not None
                },
                'classification_method': 'ml_hybrid' if zeroshot_prediction is not None else 'rule_based'
            }

        except Exception as e:
            logger.error(f"Classification error: {e}", exc_info=True)
            return {
                'contains_phi': False,
                'confidence': 0.0,
                'phi_score': 0.0,
                'error': str(e),
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }

    def batch_classify(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Classify multiple documents efficiently
        """
        results = []
        for i, text in enumerate(texts):
            if i % 10 == 0:
                logger.info(f"Processing document {i+1}/{len(texts)}")

            result = self.classify_document(text)
            results.append(result)

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded models
        """
        return {
            'models_available': {
                'ner': self.ner_model is not None,
                'text_classifier': self.text_classifier is not None,
                'clinical_embeddings': self.embeddings_model is not None
            },
            'model_details': {
                'ner': 'd4data/biomedical-ner-all (or fallback)' if self.ner_model else 'Not loaded',
                'classifier': 'facebook/bart-large-mnli (zero-shot)' if self.text_classifier else 'Not loaded',
                'embeddings': 'emilyalsentzer/Bio_ClinicalBERT' if self.embeddings_model else 'Not loaded'
            },
            'is_trained': self.is_trained,
            'cache_dir': str(self.model_manager.cache_dir)
        }

    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate that the classifier is properly set up
        """
        issues = []
        warnings_list = []

        if not HAS_TRANSFORMERS:
            issues.append("Transformers library not installed - ML features disabled")

        if self.ner_model is None:
            warnings_list.append("NER model not available - entity recognition disabled")

        if self.text_classifier is None:
            warnings_list.append("Text classifier not available - falling back to rule-based")

        if self.embeddings_model is None:
            warnings_list.append("Clinical embeddings not available - feature set limited")

        is_operational = len(issues) == 0

        return {
            'operational': is_operational,
            'has_ml_models': self.ner_model is not None or self.text_classifier is not None,
            'issues': issues,
            'warnings': warnings_list,
            'recommendation': 'Install transformers and torch for full ML capabilities' if not HAS_TRANSFORMERS else 'System ready'
        }
