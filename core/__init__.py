"""
PHI Classifier Core Module

This package contains the core functionality for PHI classification:
- HIPAA identifier detection
- Machine learning classification
- Synthetic data generation
- Security management
"""

__version__ = '1.0.0'
__author__ = 'FredHutch PHI Classifier Team'

from .hipaa_identifier import HIPAAIdentifier
from .classifier import AdvancedPHIClassifier
from .generator import SyntheticHealthDataGenerator
from .security import SecurityManager

__all__ = [
    'HIPAAIdentifier',
    'AdvancedPHIClassifier', 
    'SyntheticHealthDataGenerator',
    'SecurityManager'
]
