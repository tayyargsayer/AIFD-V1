"""
Application Constants - Clean Code Practice

This file contains all magic strings and numbers used throughout the application.
Following clean code principles, all literal values should be defined here as constants
to improve maintainability, readability, and reduce errors.

Author: AI Project Generator Team
Date: 2025
"""

# =============================================================================
# UI CONSTANTS
# =============================================================================

DEFAULT_PROJECT_DESCRIPTION = "Henüz bir proje açıklaması girilmedi."

# Page Configuration
PAGE_TITLE = "Öğrenci Proje Fikri Üretici"
PAGE_ICON = "🎓"
LAYOUT_WIDE = "wide"
SIDEBAR_EXPANDED = "expanded"

# Headers and Titles
MAIN_HEADER = "🚀 Proje Öneriniz"
CHAT_HEADER = "💬 Proje Hakkında Sohbet"
MODEL_SETTINGS_TITLE = "⚙️ Model Ayarları"
SECURITY_SETTINGS_TITLE = "🛡️ Güvenlik Ayarları"

# Form Labels
FORM_KEY = "project_generator_form"
SUBMIT_BUTTON_TEXT = "Proje Fikirleri Üret"
BACK_BUTTON_TEXT = "← Proje Üreticiye Geri Dön"

# Input Form Labels
DETAILED_INFO_LABEL = "Proje Hakkında Detaylı Bilgi"
DETAILED_INFO_PLACEHOLDER = "Projenizle ilgili detayları yazın..."
DETAILED_INFO_HELP = "Projeniz hakkında ne kadar çok detay verirseniz, o kadar özelleştirilmiş öneriler alırsınız."

CATEGORIES_LABEL = "Proje Kategorileri"
CATEGORIES_HELP = "İlgilendiğiniz proje kategorilerini seçin."

DIFFICULTY_LABEL = "Zorluk Seviyesi"
DIFFICULTY_HELP = "Projenin zorluk seviyesini seçin."

PROJECT_TYPE_LABEL = "Proje Tipi"
PROJECT_TYPE_HELP = "Projenin tipini seçin."

INTERESTS_LABEL = "İlgi Alanları"
INTERESTS_HELP = "İlgilendiğiniz alanları seçin."

KEYWORDS_LABEL = "Anahtar Kelimeler"
KEYWORDS_PLACEHOLDER = "Ör: e-ticaret, veri analizi, oyun..."
KEYWORDS_HELP = "Projenizle ilgili anahtar kelimeleri girin."

TIMELINE_LABEL = "Proje Zaman Çizelgesi (Hafta)"
TIMELINE_HELP = "Projeyi tamamlamak için düşündüğünüz süreyi seçin."

COMPLEXITY_LABEL = "Proje Karmaşıklığı"
COMPLEXITY_HELP = "Projenin karmaşıklık seviyesini seçin (1: Basit, 10: Çok karmaşık)."

FILE_UPLOAD_LABEL = "İlham için Dosya Yükleyin (İsteğe Bağlı)"

# Model Configuration Labels
TEMPERATURE_LABEL = "Yaratıcılık (Temperature)"
TEMPERATURE_HELP = "Daha yüksek değerler daha yaratıcı sonuçlar üretir."

MAX_TOKENS_LABEL = "Maksimum Çıktı Uzunluğu"
MAX_TOKENS_HELP = "Daha yüksek değerler daha uzun ve detaylı yanıtlar üretir."

SAFETY_LEVEL_LABEL = "Güvenlik Seviyesi"
SAFETY_LEVEL_HELP = "Güvenlik filtrelerinin hassasiyeti. Minimum seviye daha az engelleme yapar."

# Button Labels
SAVE_PROJECT_BUTTON = "💾 Projeyi Kaydet"
DOWNLOAD_MARKDOWN_BUTTON = "📥 Markdown Olarak İndir"
START_CHAT_BUTTON = "💬 Sohbete Başla"

# Chat Interface Labels
CHAT_INPUT_PLACEHOLDER = "Sorunuzu yazın..."

# =============================================================================
# STATUS MESSAGES
# =============================================================================

# Project Generation Status Messages
STATUS_GENERATING = "🚀 Proje fikirleri oluşturuluyor..."
STATUS_PROCESSING_INPUTS = "⚙️ Girişler işleniyor..."
STATUS_PROCESSING_IMAGE = "🖼️ Yüklenen dosya işleniyor..."
STATUS_CREATING_PROMPT = "📝 Özelleştirilmiş istek oluşturuluyor..."
STATUS_CONNECTING_API = "🤖 Gemini API'ye bağlanılıyor..."
STATUS_GENERATING_IDEAS = "🧠 Proje fikirleri üretiliyor... (Bu biraz zaman alabilir)"
STATUS_PREPARING_RESULTS = "✅ Sonuçlar hazırlanıyor..."
STATUS_PROJECT_COMPLETE = "🎉 Proje rehberi başarıyla oluşturuldu!"
STATUS_PROJECT_READY = "✅ Proje rehberi hazır!"

# Chat Status Messages
STATUS_CHAT_PREPARING = "🤖 Yanıt hazırlanıyor..."
STATUS_CHAT_ANALYZING = "📝 Sorunuz analiz ediliyor..."
STATUS_CHAT_GENERATING = "🧠 Detaylı yanıt oluşturuluyor..."
STATUS_CHAT_READY = "✅ Yanıt hazır!"
STATUS_CHAT_COMPLETE = "✅ Yanıt tamamlandı!"
STATUS_CHAT_ERROR = "❌ Hata oluştu"

# Success Messages
SUCCESS_PROJECT_SAVED = "Proje başarıyla kaydedildi!"

# Warning Messages
WARNING_FILL_REQUIRED_FIELDS = "Lütfen proje fikrinizle ilgili en az bir alanı doldurun (Proje Detayları, Anahtar Kelimeler, Kategoriler veya İlgi Alanları)."

# Info Messages
INFO_CHAT_WELCOME = ("Proje hakkında daha fazla bilgi almak için sorular sorabilirsiniz. "
                    "Örneğin: 'Bu projeyi nasıl başlatabilirim?' veya 'Hangi kütüphaneler gerekli?'")

# Error Messages
ERROR_PROJECT_SAVE = "Proje kaydedilirken bir hata oluştu."

# =============================================================================
# NUMERIC CONSTANTS
# =============================================================================

# Timing Constants (in seconds)
DELAY_SHORT = 0.3
DELAY_MEDIUM = 0.5
DELAY_LONG = 1.0

# Slider Ranges
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.0
TEMPERATURE_DEFAULT = 0.7
TEMPERATURE_STEP = 0.05

MAX_TOKENS_MIN = 1024
MAX_TOKENS_MAX = 8192
MAX_TOKENS_STEP = 256

TIMELINE_MIN = 1
TIMELINE_MAX = 16
TIMELINE_DEFAULT = 8
TIMELINE_STEP = 1

COMPLEXITY_MIN = 1
COMPLEXITY_MAX = 10
COMPLEXITY_DEFAULT = 5
COMPLEXITY_STEP = 1

# Text Lengths
MIN_RESPONSE_LENGTH_CHAT = 200
MIN_RESPONSE_LENGTH_GENERAL = 250

# =============================================================================
# SAFETY LEVELS
# =============================================================================

SAFETY_MINIMUM = "Minimum (BLOCK_NONE)"
SAFETY_LOW = "Düşük (BLOCK_ONLY_HIGH)"
SAFETY_MEDIUM = "Orta (BLOCK_MEDIUM_AND_ABOVE)"
SAFETY_HIGH = "Yüksek (BLOCK_LOW_AND_ABOVE)"

SAFETY_LEVELS = [SAFETY_MINIMUM, SAFETY_LOW, SAFETY_MEDIUM, SAFETY_HIGH]

# =============================================================================
# HTML/CSS CLASSES
# =============================================================================

CSS_SUB_HEADER = "sub-header"
CSS_SECTION_TITLE = "##### **{title}**"

# Section Titles
SECTION_CATEGORY = "Alan ve Kategori"
SECTION_SCOPE = "Kapsam ve Seviye"

# =============================================================================
# FILE EXTENSIONS
# =============================================================================

MARKDOWN_EXTENSION = ".md"
JSON_EXTENSION = ".json"

# File Upload Help Text
FILE_UPLOAD_HELP = "İzin verilen dosya türleri: {allowed_types}"

# =============================================================================
# COMPLEXITY DESCRIPTIONS
# =============================================================================

COMPLEXITY_DESCRIPTIONS = {
    1: "Çok basit - Temel kavramlar ve basit yapılar",
    2: "Basit - Temel programlama becerileri gerektirir",
    3: "Kolay - Birkaç teknoloji birlikte kullanılır",
    4: "Orta-Kolay - Birden fazla bileşen entegrasyonu",
    5: "Orta - Veri yönetimi ve API kullanımı",
    6: "Orta-Zor - Karmaşık veri yapıları ve algoritmalar",
    7: "Zor - İleri seviye mimari ve tasarım desenleri",
    8: "Çok Zor - Performans optimizasyonu ve ölçeklenebilirlik",
    9: "Uzman - Dağıtık sistemler ve mikroservisler",
    10: "Profesyonel - Endüstri seviyesi çözümler"
}

# =============================================================================
# SESSION STATE KEYS
# =============================================================================

SESSION_SHOW_CHAT = "show_chat"
SESSION_PROJECT_DATA = "project_data"
SESSION_PROJECT_CONTEXT = "project_context"
SESSION_MODEL_CONFIG = "model_config"
SESSION_MESSAGES = "messages"
SESSION_GEMINI_CLIENT = "gemini_client"

# =============================================================================
# CHAT HELP CONTENT
# =============================================================================

CHAT_HELP_TITLE = "### Sohbet Yardımı"
CHAT_HELP_CONTENT = """
Bu sohbet arayüzünü kullanarak projeniz hakkında daha fazla bilgi alabilirsiniz. İşte bazı örnek sorular:

- Bu projeyi nasıl başlatabilirim?
- Hangi programlama dilleri ve kütüphaneler gerekli?
- Projenin zorluk seviyesini biraz daha açıklayabilir misin?
- Bu projeyi bir portfolyo projesine nasıl dönüştürebilirim?
- Projeyi daha basit/karmaşık hale getirmek için ne yapabilirim?
- Bu projeyi geliştirmek için hangi kaynakları önerirsin?
- Projeyi tamamlamak için bir zaman çizelgesi önerir misin?

Yardımcı yapay zeka, projenizle ilgili sorularınızı yanıtlamak için elinden geleni yapacaktır.
"""

# =============================================================================
# TAB NAMES
# =============================================================================

TAB_CHAT = "💬 Sohbet"
TAB_HELP = "ℹ️ Yardım"

# =============================================================================
# MARKDOWN FORMATTING
# =============================================================================

MARKDOWN_DIVIDER = "---"
MARKDOWN_BOLD_FORMAT = "**{text}**"

# =============================================================================
# DEFAULT VALUES
# =============================================================================

DEFAULT_EMPTY_STRING = ""
DEFAULT_EMPTY_LIST = []
DEFAULT_ZERO = 0
DEFAULT_NONE = None

# =============================================================================
# USER ROLES
# =============================================================================

USER_ROLE = "user"
ASSISTANT_ROLE = "assistant"

# =============================================================================
# VALIDATION MESSAGES
# =============================================================================

VALIDATION_REQUIRED_FIELD = "Bu alan zorunludur"
VALIDATION_MIN_LENGTH = "Minimum {min_length} karakter gereklidir"
VALIDATION_MAX_LENGTH = "Maksimum {max_length} karakter olmalıdır"

WELCOME_MESSAGE = "Hoş geldiniz! Proje fikri üretmek için formu doldurun ve 'Proje Fikirleri Üret' butonuna tıklayın." 