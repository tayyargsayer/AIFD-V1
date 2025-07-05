"""
Configuration settings for the Student Project Generator application.
"""
import os
from typing import Dict, Any, List

# Constants
DEFAULT_MODEL_NAME = "gemini-2.5-flash"
FALLBACK_MODEL_NAME = "gemini-1.5-flash"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 8192
DEFAULT_TOP_P = 0.95
DEFAULT_TOP_K = 40

# File size limits (in bytes)
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

# Text input limits
MIN_TEXT_LENGTH = 10
MAX_TEXT_LENGTH = 2000

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 10

# UI Constants
THEME_COLOR = "#1E88E5"
SECONDARY_COLOR = "#0D47A1"
SUCCESS_COLOR = "#43A047"
WARNING_COLOR = "#FFA000"
ERROR_COLOR = "#E53935"

class AppConfig:
    """
    Application configuration settings.
    """
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Model Configuration
    DEFAULT_MODEL = DEFAULT_MODEL_NAME
    FALLBACK_MODEL = FALLBACK_MODEL_NAME
    DEFAULT_TEMPERATURE = DEFAULT_TEMPERATURE
    DEFAULT_MAX_TOKENS = DEFAULT_MAX_TOKENS
    
    # File Upload Limits
    MAX_FILE_SIZE = MAX_FILE_SIZE
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf', 'txt', 'docx']
    
    # Text Input Limits
    MAX_TEXT_LENGTH = MAX_TEXT_LENGTH
    MIN_TEXT_LENGTH = MIN_TEXT_LENGTH
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = MAX_REQUESTS_PER_MINUTE
    
    # UI Configuration
    THEME_COLOR = THEME_COLOR
    
    # Project Categories
    PROJECT_CATEGORIES = [
        "Web Geliştirme", 
        "Mobil Uygulama", 
        "Veri Bilimi", 
        "Yapay Zeka/Makine Öğrenimi", 
        "Oyun Geliştirme", 
        "IoT (Nesnelerin İnterneti)", 
        "Siber Güvenlik", 
        "Blok Zinciri", 
        "Artırılmış/Sanal Gerçeklik", 
        "Diğer"
    ]
    
    # Difficulty Levels
    DIFFICULTY_LEVELS = ["Başlangıç", "Orta", "İleri"]
    
    # Project Types
    PROJECT_TYPES = ["Kişisel", "Takım", "Akademik"]
    
    # Areas of Interest
    AREAS_OF_INTEREST = [
        "Web Geliştirme",
        "Mobil Uygulama Geliştirme",
        "Veri Bilimi",
        "Yapay Zeka/Makine Öğrenimi",
        "Oyun Geliştirme",
        "IoT (Nesnelerin İnterneti)",
        "Siber Güvenlik",
        "Blok Zinciri",
        "Artırılmış/Sanal Gerçeklik",
        "Robotik",
        "Bulut Bilişim",
        "DevOps",
        "Gömülü Sistemler",
        "Ağ Teknolojileri",
        "Veritabanı Yönetimi",
        "UI/UX Tasarımı"
    ]
    
    # Error Messages (in Turkish)
    ERROR_MESSAGES = {
        "api_key_missing": "API anahtarı eksik. Lütfen .env dosyasına GEMINI_API_KEY ekleyin.",
        "api_error": "API hatası oluştu: {error}",
        "input_too_short": "Lütfen daha fazla bilgi girin (en az {min_length} karakter).",
        "input_too_long": "Girdi çok uzun (maksimum {max_length} karakter).",
        "file_too_large": "Dosya çok büyük (maksimum {max_size}MB).",
        "invalid_file_type": "Geçersiz dosya türü. İzin verilen türler: {allowed_types}",
        "rate_limit": "Çok fazla istek gönderildi. Lütfen {retry_after} saniye sonra tekrar deneyin.",
        "general_error": "Bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
        "quota_limit": "API kota sınırına ulaşıldı. Alternatif model kullanılıyor."
    }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """
        Validate all configuration settings
        
        Returns:
            Dict[str, Any]: Status of configuration settings
        """
        config_status = {
            'api_key_present': bool(cls.GEMINI_API_KEY),
            'file_limits_set': bool(cls.MAX_FILE_SIZE),
            'valid_extensions': bool(cls.ALLOWED_EXTENSIONS)
        }
        return config_status 