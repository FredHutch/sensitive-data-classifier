"""
Security Manager

HIPAA-compliant security management system providing:
- Secure file handling and validation
- Encryption and hashing capabilities  
- Access control and audit logging
- Input sanitization and validation
"""

import os
import re
import hashlib
import secrets
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import uuid

# Cryptography imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Comprehensive security manager for HIPAA-compliant operations
    """
    
    def __init__(self):
        self.secret_key = secrets.token_hex(32)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = {'.txt', '.docx', '.pdf', '.csv', '.xlsx', '.json'}
        self.secure_directories = self._initialize_secure_directories()
        
        # Initialize encryption if available
        if HAS_CRYPTOGRAPHY:
            self._initialize_encryption()
        
        # Security patterns for content validation
        self.security_patterns = self._initialize_security_patterns()
        
        logger.info("Security Manager initialized with HIPAA-compliant settings")
    
    def _initialize_secure_directories(self) -> Dict[str, Path]:
        """
        Initialize secure directories with proper permissions
        """
        try:
            base_path = Path('/opt/phi-classifier')
        except:
            # Fallback to current directory if /opt is not accessible
            base_path = Path.cwd() / 'phi_classifier_data'
        
        directories = {
            'uploads': base_path / 'secure_uploads',
            'processed': base_path / 'processed_files',
            'logs': base_path / 'secure_logs',
            'temp': base_path / 'temp_files',
            'keys': base_path / 'encryption_keys',
            'models': base_path / 'trained_models'
        }
        
        for name, path in directories.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
                # Set secure permissions (owner read/write only)
                os.chmod(path, 0o700)
                logger.info(f"Secure directory created: {path}")
            except Exception as e:
                logger.error(f"Failed to create secure directory {path}: {e}")
                # Fallback to system temp directory
                temp_dir = Path(tempfile.gettempdir()) / f'phi_classifier_{name}'
                temp_dir.mkdir(exist_ok=True)
                directories[name] = temp_dir
        
        return directories
    
    def _initialize_encryption(self):
        """
        Initialize encryption capabilities
        """
        try:
            # Generate or load encryption key
            key_file = self.secure_directories['keys'] / 'master.key'
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                os.chmod(key_file, 0o600)  # Owner read/write only
            
            self.cipher_suite = Fernet(key)
            logger.info("Encryption system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            self.cipher_suite = None
    
    def _initialize_security_patterns(self) -> Dict[str, List[str]]:
        """
        Initialize security validation patterns
        """
        return {
            'malicious_patterns': [
                r'<script[^>]*>.*?</script>',
                r'javascript:',
                r'vbscript:',
                r'onload\s*=',
                r'onerror\s*=',
                r'eval\s*\(',
                r'exec\s*\(',
                r'\.\./.*\.\.',  # Path traversal
                r'\\\\.*\\\\',  # UNC paths
            ],
            'suspicious_content': [
                r'password\s*[:=]\s*[^\s]+',
                r'api_key\s*[:=]\s*[^\s]+',
                r'secret\s*[:=]\s*[^\s]+',
                r'token\s*[:=]\s*[^\s]+'
            ],
            'phi_patterns': [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
                r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'  # Dates
            ]
        }
    
    def validate_file(self, file_obj) -> bool:
        """
        Comprehensive file validation
        
        Args:
            file_obj: File object or file path to validate
            
        Returns:
            bool: True if file is valid and safe
        """
        try:
            # Get filename and size
            if hasattr(file_obj, 'filename'):
                filename = file_obj.filename
                file_obj.seek(0, 2)  # Seek to end
                file_size = file_obj.tell()
                file_obj.seek(0)  # Reset to beginning
            elif isinstance(file_obj, str):
                filename = file_obj
                file_size = os.path.getsize(file_obj) if os.path.exists(file_obj) else 0
            else:
                logger.warning("Invalid file object provided")
                return False
            
            # Validate filename
            if not self.is_safe_filename(filename):
                logger.warning(f"Unsafe filename: {filename}")
                return False
            
            # Validate file extension
            if not self.validate_file_type(filename):
                logger.warning(f"Invalid file type: {filename}")
                return False
            
            # Validate file size
            if file_size > self.max_file_size:
                logger.warning(f"File size exceeds limit: {file_size} > {self.max_file_size}")
                return False
            
            # Content validation if accessible
            if hasattr(file_obj, 'read'):
                content_sample = file_obj.read(1024).decode('utf-8', errors='ignore')
                file_obj.seek(0)  # Reset
                
                is_safe, threats = self.validate_content_security(content_sample)
                if not is_safe:
                    logger.warning(f"Content security validation failed: {threats}")
                    return False
            
            self.log_security_event("file_validated", {
                'filename': filename,
                'file_size': file_size,
                'validation_result': 'PASSED'
            })
            
            return True
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            self.log_security_event("file_validation_error", {
                'filename': getattr(file_obj, 'filename', 'unknown'),
                'error': str(e)
            })
            return False
    
    def validate_file_type(self, filename: str) -> bool:
        """
        Validate file extension against allowed types
        
        Args:
            filename (str): Filename to validate
            
        Returns:
            bool: True if file type is allowed
        """
        if not filename:
            return False
        
        file_extension = Path(filename).suffix.lower()
        return file_extension in self.allowed_extensions
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename to prevent security issues
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        if not filename:
            return "unnamed_file.txt"
        
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '_', sanitized)
        
        # Limit length
        sanitized = sanitized[:255]
        
        # Ensure it has a valid extension
        if '.' not in sanitized:
            sanitized += '.txt'
        
        return sanitized
    
    def is_safe_filename(self, filename: str) -> bool:
        """
        Check if filename is safe for use
        
        Args:
            filename (str): Filename to check
            
        Returns:
            bool: True if filename is safe
        """
        if not filename or filename in ['.', '..']:
            return False
        
        # Check for path traversal attempts
        if '..' in filename or filename.startswith('/'):
            return False
        
        # Check for reserved names (Windows compatibility)
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'LPT1'}
        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    def validate_content_security(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate content for security threats
        
        Args:
            content (str): Content to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_safe, list_of_threats_found)
        """
        threats_found = []
        
        try:
            # Check for malicious patterns
            for pattern in self.security_patterns['malicious_patterns']:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    threats_found.append(f"Malicious pattern: {pattern}")
            
            # Check for suspicious content (but don't block, just warn)
            for pattern in self.security_patterns['suspicious_content']:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    logger.warning(f"Suspicious content pattern found: {pattern}")
            
            is_safe = len(threats_found) == 0
            
            if not is_safe:
                logger.warning(f"Content security validation failed: {threats_found}")
            
            return is_safe, threats_found
            
        except Exception as e:
            logger.error(f"Content security validation error: {e}")
            return False, [f"Validation error: {e}"]
    
    def generate_document_id(self) -> str:
        """
        Generate secure document identifier
        
        Returns:
            str: Unique document ID
        """
        return str(uuid.uuid4())
    
    def generate_file_hash(self, content: bytes) -> str:
        """
        Generate SHA-256 hash of file content
        
        Args:
            content (bytes): File content
            
        Returns:
            str: SHA-256 hash
        """
        return hashlib.sha256(content).hexdigest()
    
    def encrypt_content(self, content: str) -> Optional[bytes]:
        """
        Encrypt content using Fernet encryption
        
        Args:
            content (str): Content to encrypt
            
        Returns:
            Optional[bytes]: Encrypted content or None if encryption fails
        """
        if not HAS_CRYPTOGRAPHY or not hasattr(self, 'cipher_suite') or not self.cipher_suite:
            logger.warning("Encryption not available")
            return None
        
        try:
            return self.cipher_suite.encrypt(content.encode('utf-8'))
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None
    
    def decrypt_content(self, encrypted_content: bytes) -> Optional[str]:
        """
        Decrypt content using Fernet encryption
        
        Args:
            encrypted_content (bytes): Encrypted content
            
        Returns:
            Optional[str]: Decrypted content or None if decryption fails
        """
        if not HAS_CRYPTOGRAPHY or not hasattr(self, 'cipher_suite') or not self.cipher_suite:
            logger.warning("Encryption not available")
            return None
        
        try:
            return self.cipher_suite.decrypt(encrypted_content).decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None
    
    def secure_file_storage(self, content: bytes, filename: str) -> Optional[str]:
        """
        Store file securely with encryption
        
        Args:
            content (bytes): File content
            filename (str): Original filename
            
        Returns:
            Optional[str]: Secure file path or None if storage fails
        """
        try:
            # Generate secure filename
            file_id = self.generate_document_id()
            secure_filename = f"{file_id}_{self.sanitize_filename(filename)}"
            secure_path = self.secure_directories['processed'] / secure_filename
            
            # Encrypt content if available
            if HAS_CRYPTOGRAPHY and hasattr(self, 'cipher_suite') and self.cipher_suite:
                encrypted_content = self.cipher_suite.encrypt(content)
                storage_content = encrypted_content
            else:
                storage_content = content
            
            # Write to secure location
            with open(secure_path, 'wb') as f:
                f.write(storage_content)
            
            # Set secure permissions
            os.chmod(secure_path, 0o600)
            
            # Log the storage operation
            self.log_security_event("file_stored", {
                'filename': filename,
                'secure_path': str(secure_path),
                'file_hash': self.generate_file_hash(content),
                'encrypted': HAS_CRYPTOGRAPHY and hasattr(self, 'cipher_suite') and self.cipher_suite is not None
            })
            
            return str(secure_path)
            
        except Exception as e:
            logger.error(f"Secure file storage error: {e}")
            return None
    
    def log_security_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Log security events for audit trail
        
        Args:
            event_type (str): Type of security event
            event_data (Dict): Event-specific data
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'event_data': event_data,
                'session_id': getattr(self, 'session_id', 'unknown')
            }
            
            # Write to secure log file
            log_file = self.secure_directories['logs'] / 'security_audit.log'
            with open(log_file, 'a') as f:
                f.write(f"{json.dumps(log_entry)}\n")
            
            # Also log to standard logger
            logger.info(f"Security Event [{event_type}]: {event_data}")
            
        except Exception as e:
            logger.error(f"Security logging error: {e}")
    
    def create_temp_file(self, content: bytes, suffix: str = '.tmp') -> Optional[str]:
        """
        Create temporary file with secure handling
        
        Args:
            content (bytes): File content
            suffix (str): File extension
            
        Returns:
            Optional[str]: Temporary file path or None if creation fails
        """
        try:
            temp_file = tempfile.NamedTemporaryFile(
                dir=self.secure_directories['temp'],
                suffix=suffix,
                delete=False
            )
            
            temp_file.write(content)
            temp_file.close()
            
            # Set secure permissions
            os.chmod(temp_file.name, 0o600)
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Temporary file creation error: {e}")
            return None
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        Clean up old temporary files
        
        Args:
            max_age_hours (int): Maximum age of temp files in hours
        """
        try:
            temp_dir = self.secure_directories['temp']
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            cleaned_count = 0
            for temp_file in temp_dir.glob('*'):
                if temp_file.is_file():
                    file_time = datetime.fromtimestamp(temp_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        temp_file.unlink()
                        cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old temp files")
                self.log_security_event("temp_files_cleaned", {'count': cleaned_count})
            
        except Exception as e:
            logger.error(f"Temp file cleanup error: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security system status
        
        Returns:
            Dict[str, Any]: Security status information
        """
        temp_files_count = 0
        log_files_count = 0
        
        try:
            temp_files_count = len(list(self.secure_directories['temp'].glob('*')))
            log_files_count = len(list(self.secure_directories['logs'].glob('*.log')))
        except:
            pass
        
        return {
            'encryption_available': HAS_CRYPTOGRAPHY and hasattr(self, 'cipher_suite') and self.cipher_suite is not None,
            'secure_directories': {k: str(v) for k, v in self.secure_directories.items()},
            'max_file_size': self.max_file_size,
            'allowed_extensions': list(self.allowed_extensions),
            'security_patterns_loaded': len(self.security_patterns['malicious_patterns']),
            'temp_files_count': temp_files_count,
            'log_files_count': log_files_count,
            'initialization_time': datetime.now().isoformat()
        }
    
    def validate_phi_content(self, text: str) -> Dict[str, Any]:
        """
        Validate content for PHI patterns (for testing/analysis purposes)
        
        Args:
            text (str): Text content to analyze
            
        Returns:
            Dict[str, Any]: PHI validation results
        """
        phi_indicators = {}
        total_matches = 0
        
        for pattern in self.security_patterns['phi_patterns']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                phi_indicators[pattern] = matches
                total_matches += len(matches)
        
        return {
            'phi_indicators_found': phi_indicators,
            'total_phi_matches': total_matches,
            'likely_contains_phi': total_matches > 0,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def __del__(self):
        """
        Cleanup on destruction
        """
        try:
            # Clean up temp files on exit
            self.cleanup_temp_files(max_age_hours=1)
        except:
            pass  # Ignore errors during cleanup

import json