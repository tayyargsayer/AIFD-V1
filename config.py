# config.py
import os
from typing import Dict, Any

class AppConfig:
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # File Upload Limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'webp']
    
    # Text Input Limits
    MAX_TEXT_LENGTH = 2000
    MIN_TEXT_LENGTH = 10
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 10
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate all configuration settings"""
        config_status = {
            'api_key_present': bool(cls.GEMINI_API_KEY),
            'file_limits_set': bool(cls.MAX_FILE_SIZE),
            'valid_extensions': bool(cls.ALLOWED_EXTENSIONS)
        }
        return config_status 