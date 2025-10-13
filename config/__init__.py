"""
Configuration Package

Provides environment-based configuration management for the PHI classifier application.
"""

from .settings import (
    Config,
    DevelopmentConfig,
    TestingConfig,
    StagingConfig,
    ProductionConfig,
    get_config,
    setup_logging,
    validate_config,
    config
)

__all__ = [
    'Config',
    'DevelopmentConfig', 
    'TestingConfig',
    'StagingConfig',
    'ProductionConfig',
    'get_config',
    'setup_logging',
    'validate_config',
    'config'
]
