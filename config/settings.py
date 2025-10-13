"""
Configuration Management System

Environment-based configuration management for PHI classifier application.
Supports development, testing, staging, and production environments with
secure credential management and feature flags.

Features:
- Environment-specific configurations
- Secure credential management
- Database connection settings
- API configuration
- Feature flags and toggles
- Logging configuration
- Security settings
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import logging

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = 'localhost'
    port: int = 5432
    database: str = 'phi_classifier'
    username: str = 'phi_user'
    password: str = ''
    ssl_mode: str = 'prefer'
    connection_timeout: int = 30
    max_connections: int = 20
    
@dataclass
class RedisConfig:
    """Redis cache configuration settings."""
    host: str = 'localhost'
    port: int = 6379
    database: int = 0
    password: str = ''
    ssl: bool = False
    connection_timeout: int = 10
    max_connections: int = 50
    
@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = 'change-me-in-production'
    encryption_key: str = ''
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = None
    session_timeout: int = 3600  # 1 hour
    password_min_length: int = 12
    enable_audit_logging: bool = True
    cors_origins: list = None
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.txt', '.docx', '.pdf', '.csv', '.xlsx', '.json']
        if self.cors_origins is None:
            self.cors_origins = ['http://localhost:3000', 'http://localhost:5000']

@dataclass
class UMLSConfig:
    """UMLS integration configuration."""
    api_key: str = ''
    base_url: str = 'https://uts-ws.nlm.nih.gov/rest'
    enable_caching: bool = True
    cache_ttl: int = 86400  # 24 hours
    max_requests_per_minute: int = 100
    timeout: int = 30
    
@dataclass
class ModelConfig:
    """Machine learning model configuration."""
    model_dir: str = './models'
    enable_training: bool = True
    batch_size: int = 32
    max_features: int = 15000
    cross_validation_folds: int = 5
    enable_hyperparameter_tuning: bool = True
    model_cache_size: int = 5
    prediction_threshold: float = 0.5
    
class Config:
    """
    Base configuration class with common settings.
    """
    
    def __init__(self):
        # Application settings
        self.APP_NAME = 'PHI Classifier'
        self.VERSION = '1.0.0'
        self.DEBUG = self._get_bool_env('DEBUG', False)
        self.TESTING = self._get_bool_env('TESTING', False)
        
        # Server settings
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 5000))
        self.WORKERS = int(os.getenv('WORKERS', 4))
        
        # Path settings
        self.BASE_DIR = Path(__file__).parent.parent
        self.UPLOAD_DIR = self.BASE_DIR / 'uploads'
        self.LOG_DIR = self.BASE_DIR / 'logs'
        self.DATA_DIR = self.BASE_DIR / 'data'
        
        # Create directories if they don't exist
        for directory in [self.UPLOAD_DIR, self.LOG_DIR, self.DATA_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configuration objects
        self.database = self._load_database_config()
        self.redis = self._load_redis_config()
        self.security = self._load_security_config()
        self.umls = self._load_umls_config()
        self.model = self._load_model_config()
        
        # Feature flags
        self.features = self._load_feature_flags()
        
        # Logging configuration
        self.logging = self._load_logging_config()
        
    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, '').lower()
        return value in ('true', '1', 'yes', 'on') if value else default
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment."""
        return DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'phi_classifier'),
            username=os.getenv('DB_USER', 'phi_user'),
            password=os.getenv('DB_PASSWORD', ''),
            ssl_mode=os.getenv('DB_SSL_MODE', 'prefer'),
            connection_timeout=int(os.getenv('DB_TIMEOUT', 30)),
            max_connections=int(os.getenv('DB_MAX_CONNECTIONS', 20))
        )
    
    def _load_redis_config(self) -> RedisConfig:
        """Load Redis configuration from environment."""
        return RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            database=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD', ''),
            ssl=self._get_bool_env('REDIS_SSL', False),
            connection_timeout=int(os.getenv('REDIS_TIMEOUT', 10)),
            max_connections=int(os.getenv('REDIS_MAX_CONNECTIONS', 50))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment."""
        allowed_types = os.getenv('ALLOWED_FILE_TYPES', '').split(',') if os.getenv('ALLOWED_FILE_TYPES') else None
        cors_origins = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else None
        
        return SecurityConfig(
            secret_key=os.getenv('SECRET_KEY', 'change-me-in-production'),
            encryption_key=os.getenv('ENCRYPTION_KEY', ''),
            max_file_size=int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024)),
            allowed_file_types=[t.strip() for t in allowed_types] if allowed_types else None,
            session_timeout=int(os.getenv('SESSION_TIMEOUT', 3600)),
            password_min_length=int(os.getenv('PASSWORD_MIN_LENGTH', 12)),
            enable_audit_logging=self._get_bool_env('ENABLE_AUDIT_LOGGING', True),
            cors_origins=[o.strip() for o in cors_origins] if cors_origins else None
        )
    
    def _load_umls_config(self) -> UMLSConfig:
        """Load UMLS configuration from environment."""
        return UMLSConfig(
            api_key=os.getenv('UMLS_API_KEY', ''),
            base_url=os.getenv('UMLS_BASE_URL', 'https://uts-ws.nlm.nih.gov/rest'),
            enable_caching=self._get_bool_env('UMLS_ENABLE_CACHING', True),
            cache_ttl=int(os.getenv('UMLS_CACHE_TTL', 86400)),
            max_requests_per_minute=int(os.getenv('UMLS_MAX_REQUESTS', 100)),
            timeout=int(os.getenv('UMLS_TIMEOUT', 30))
        )
    
    def _load_model_config(self) -> ModelConfig:
        """Load model configuration from environment."""
        return ModelConfig(
            model_dir=os.getenv('MODEL_DIR', './models'),
            enable_training=self._get_bool_env('ENABLE_MODEL_TRAINING', True),
            batch_size=int(os.getenv('MODEL_BATCH_SIZE', 32)),
            max_features=int(os.getenv('MODEL_MAX_FEATURES', 15000)),
            cross_validation_folds=int(os.getenv('MODEL_CV_FOLDS', 5)),
            enable_hyperparameter_tuning=self._get_bool_env('ENABLE_HYPERPARAMETER_TUNING', True),
            model_cache_size=int(os.getenv('MODEL_CACHE_SIZE', 5)),
            prediction_threshold=float(os.getenv('PREDICTION_THRESHOLD', 0.5))
        )
    
    def _load_feature_flags(self) -> Dict[str, bool]:
        """Load feature flags from environment."""
        return {
            'enable_synthetic_data_generation': self._get_bool_env('FEATURE_SYNTHETIC_DATA', True),
            'enable_batch_processing': self._get_bool_env('FEATURE_BATCH_PROCESSING', True),
            'enable_api_rate_limiting': self._get_bool_env('FEATURE_RATE_LIMITING', True),
            'enable_model_retraining': self._get_bool_env('FEATURE_MODEL_RETRAINING', False),
            'enable_advanced_analytics': self._get_bool_env('FEATURE_ADVANCED_ANALYTICS', True),
            'enable_webhook_notifications': self._get_bool_env('FEATURE_WEBHOOKS', False),
            'enable_user_authentication': self._get_bool_env('FEATURE_AUTH', False),
            'enable_document_versioning': self._get_bool_env('FEATURE_VERSIONING', True),
            'enable_performance_monitoring': self._get_bool_env('FEATURE_MONITORING', True),
            'enable_data_export': self._get_bool_env('FEATURE_DATA_EXPORT', True)
        }
    
    def _load_logging_config(self) -> Dict[str, Any]:
        """Load logging configuration."""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
                },
                'json': {
                    'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
                }
            },
            'handlers': {
                'console': {
                    'level': log_level,
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard'
                },
                'file': {
                    'level': log_level,
                    'class': 'logging.FileHandler',
                    'filename': str(self.LOG_DIR / 'application.log'),
                    'formatter': 'detailed'
                },
                'security_file': {
                    'level': 'INFO',
                    'class': 'logging.FileHandler',
                    'filename': str(self.LOG_DIR / 'security.log'),
                    'formatter': 'json'
                }
            },
            'loggers': {
                '': {  # Root logger
                    'handlers': ['console', 'file'],
                    'level': log_level,
                    'propagate': False
                },
                'security': {
                    'handlers': ['security_file', 'console'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
    
    def get_database_url(self) -> str:
        """Get database connection URL."""
        db = self.database
        return f"postgresql://{db.username}:{db.password}@{db.host}:{db.port}/{db.database}?sslmode={db.ssl_mode}"
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        redis = self.redis
        protocol = 'rediss' if redis.ssl else 'redis'
        auth = f":{redis.password}@" if redis.password else ""
        return f"{protocol}://{auth}{redis.host}:{redis.port}/{redis.database}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            'app_name': self.APP_NAME,
            'version': self.VERSION,
            'debug': self.DEBUG,
            'testing': self.TESTING,
            'host': self.HOST,
            'port': self.PORT,
            'workers': self.WORKERS,
            'features': self.features,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'ssl_mode': self.database.ssl_mode
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'database': self.redis.database,
                'ssl': self.redis.ssl
            },
            'security': {
                'max_file_size': self.security.max_file_size,
                'allowed_file_types': self.security.allowed_file_types,
                'session_timeout': self.security.session_timeout,
                'enable_audit_logging': self.security.enable_audit_logging
            },
            'model': {
                'model_dir': self.model.model_dir,
                'batch_size': self.model.batch_size,
                'max_features': self.model.max_features,
                'prediction_threshold': self.model.prediction_threshold
            }
        }

class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.security.secret_key = 'dev-secret-key-not-for-production'
        
        # Development-specific feature flags
        self.features.update({
            'enable_debug_toolbar': True,
            'enable_hot_reload': True,
            'enable_detailed_logging': True,
            'skip_security_checks': True,
            'enable_test_data': True
        })

class TestingConfig(Config):
    """Testing environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.TESTING = True
        self.database.database = 'phi_classifier_test'
        self.redis.database = 1  # Use different Redis DB for tests
        self.security.secret_key = 'test-secret-key'
        
        # Testing-specific settings
        self.security.max_file_size = 1024 * 1024  # 1MB for tests
        self.model.enable_training = False  # Disable training in tests
        
        # Testing feature flags
        self.features.update({
            'enable_test_endpoints': True,
            'skip_external_apis': True,
            'enable_mock_data': True,
            'disable_rate_limiting': True
        })

class StagingConfig(Config):
    """Staging environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        
        # Staging-specific settings
        self.security.cors_origins = [
            'https://staging-phi-classifier.example.com',
            'https://staging-api.example.com'
        ]
        
        # Staging feature flags
        self.features.update({
            'enable_performance_testing': True,
            'enable_load_testing': True,
            'enable_security_scanning': True
        })

class ProductionConfig(Config):
    """Production environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        
        # Production security hardening
        self.security.session_timeout = 1800  # 30 minutes
        self.security.password_min_length = 16
        self.security.cors_origins = [
            'https://phi-classifier.fredhutch.org',
            'https://api.fredhutch.org'
        ]
        
        # Production-specific settings
        self.WORKERS = int(os.getenv('WORKERS', 8))
        self.model.enable_hyperparameter_tuning = False  # Disable in prod for performance
        
        # Production feature flags
        self.features.update({
            'enable_production_monitoring': True,
            'enable_security_alerts': True,
            'enable_backup_systems': True,
            'enable_disaster_recovery': True
        })

def get_config(env: Optional[str] = None) -> Config:
    """Get configuration object based on environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', os.getenv('APP_ENV', 'development')).lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'dev': DevelopmentConfig,
        'testing': TestingConfig,
        'test': TestingConfig,
        'staging': StagingConfig,
        'stage': StagingConfig,
        'production': ProductionConfig,
        'prod': ProductionConfig
    }
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()

# Global configuration instance
config = get_config()

# Utility functions
def setup_logging(config_dict: Dict[str, Any]):
    """Setup logging based on configuration."""
    import logging.config
    logging.config.dictConfig(config_dict)

def validate_config(config_obj: Config) -> List[str]:
    """Validate configuration and return list of warnings/errors."""
    issues = []
    
    # Security validations
    if config_obj.security.secret_key == 'change-me-in-production':
        issues.append("WARNING: Using default secret key - change for production")
    
    if not config_obj.security.encryption_key and config_obj.features.get('enable_encryption', True):
        issues.append("WARNING: No encryption key set - encryption features disabled")
    
    # Database validations
    if not config_obj.database.password and not config_obj.TESTING:
        issues.append("WARNING: No database password set")
    
    # UMLS validations
    if not config_obj.umls.api_key:
        issues.append("INFO: No UMLS API key set - using fallback patterns")
    
    # Directory validations
    for dir_name, dir_path in [('upload', config_obj.UPLOAD_DIR), 
                               ('log', config_obj.LOG_DIR),
                               ('data', config_obj.DATA_DIR)]:
        if not dir_path.exists():
            issues.append(f"WARNING: {dir_name} directory does not exist: {dir_path}")
        elif not os.access(dir_path, os.R_OK | os.W_OK):
            issues.append(f"ERROR: Insufficient permissions for {dir_name} directory: {dir_path}")
    
    return issues