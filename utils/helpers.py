"""
Helper functions for the Student Project Generator application.
"""
import os
import json
import base64
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
import pandas as pd
from PIL import Image
import io
import streamlit as st

from config.settings import AppConfig
from config.constants import COMPLEXITY_DESCRIPTIONS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_input(text: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user input text.
    
    Args:
        text (str): Text to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not text or len(text.strip()) < AppConfig.MIN_TEXT_LENGTH:
        return False, AppConfig.ERROR_MESSAGES["input_too_short"].format(min_length=AppConfig.MIN_TEXT_LENGTH)
    
    if len(text) > AppConfig.MAX_TEXT_LENGTH:
        return False, AppConfig.ERROR_MESSAGES["input_too_long"].format(max_length=AppConfig.MAX_TEXT_LENGTH)
    
    return True, None

def validate_file(file) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Args:
        file: File object from st.file_uploader
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if file is None:
        return True, None  # File is optional
    
    # Check file size
    if file.size > AppConfig.MAX_FILE_SIZE:
        max_size_mb = AppConfig.MAX_FILE_SIZE / (1024 * 1024)
        return False, AppConfig.ERROR_MESSAGES["file_too_large"].format(max_size=max_size_mb)
    
    # Check file extension
    file_ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
    if file_ext not in AppConfig.ALLOWED_EXTENSIONS:
        return False, AppConfig.ERROR_MESSAGES["invalid_file_type"].format(
            allowed_types=', '.join(AppConfig.ALLOWED_EXTENSIONS)
        )
    
    return True, None

def create_project_prompt(user_inputs: Dict[str, Any]) -> str:
    """
    Create a comprehensive prompt for the Gemini API based on user inputs.
    
    Args:
        user_inputs (Dict[str, Any]): Dictionary of user inputs
        
    Returns:
        str: Formatted prompt for Gemini API
        
    Following clean code principles:
    - All magic strings moved to constants
    - Clear separation of data extraction and prompt generation
    """
    # Extract user inputs
    categories = user_inputs.get('categories', [])
    difficulty = user_inputs.get('difficulty', '')
    project_type = user_inputs.get('project_type', '')
    interests = user_inputs.get('interests', [])
    keywords = user_inputs.get('keywords', '')
    timeline = user_inputs.get('timeline', 0)
    complexity = user_inputs.get('complexity', 0)
    detailed_info = user_inputs.get('detailed_info', '')
    
    # Get complexity description from constants
    complexity_desc = COMPLEXITY_DESCRIPTIONS.get(complexity, "Belirtilmemiş")
    
    # Format the comprehensive prompt in Turkish
    prompt = f"""
    Sen 15+ yıl deneyimli bir senior yazılım mimarı, proje yöneticisi ve teknik mentorsun. Öğrenciler için sadece proje fikri değil, tam bir proje rehberi ve uygulama planı oluşturman gerekiyor. Yanıtın profesyonel, detaylı ve uygulanabilir olmalı.
    
    ## Öğrenci Profili ve İhtiyaçları:
    - **Detaylı Proje Açıklaması:** {detailed_info if detailed_info else 'Öğrenci genel bir proje fikri arıyor'}
    - **Hedeflenen Kategoriler:** {', '.join(categories) if categories else 'Açık'}
    - **İlgi Alanları:** {', '.join(interests) if interests else 'Çeşitli teknolojiler'}
    - **Anahtar Kelimeler:** {keywords if keywords else 'Yenilikçi çözümler'}
    - **Zorluk Seviyesi:** {difficulty if difficulty else 'Uygun seviye'}
    - **Proje Türü:** {project_type if project_type else 'Esnek'}
    - **Süre:** {timeline} hafta
    - **Karmaşıklık:** {complexity}/10 ({complexity_desc})
    
    ## KAPSAMLI PROJE REHBERİ OLUŞTUR:
    
    Aşağıdaki formatı takip ederek, her bölümü mümkün olduğunca detaylı şekilde doldur:
    
    # 🚀 [Yaratıcı ve Çekici Proje Başlığı]
    
    ## 📋 Proje Genel Bakış
    
    ### 🎯 Problem Tanımı ve Çözüm
    - Hangi gerçek dünya problemini çözüyor?
    - Mevcut çözümlerden farkı nedir?
    - Neden bu proje önemli ve değerli?
    
    ### 🌟 Proje Vizyonu
    - Projenin uzun vadeli hedefi
    - Başarı kriterleri
    - Proje tamamlandığında elde edilecek kazanımlar
    
    ## 🎯 Detaylı Proje Hedefleri
    
    ### Ana Hedefler:
    - [ ] [Hedef 1 - Spesifik ve ölçülebilir]
    - [ ] [Hedef 2 - Spesifik ve ölçülebilir]
    - [ ] [Hedef 3 - Spesifik ve ölçülebilir]
    
    ### İkincil Hedefler:
    - [ ] [Bonus özellik 1]
    - [ ] [Bonus özellik 2]
    
    ## 👥 Hedef Kitle ve Kullanım Senaryoları
    
    ### Birincil Kullanıcılar:
    - **Profil:** [Detaylı kullanıcı profili]
    - **İhtiyaçlar:** [Kullanıcı ihtiyaçları]
    - **Kullanım Sıklığı:** [Ne sıklıkla kullanacaklar]
    
    ### Kullanım Senaryoları:
    1. **Senaryo 1:** [Detaylı kullanım senaryosu]
    2. **Senaryo 2:** [Detaylı kullanım senaryosu]
    3. **Senaryo 3:** [Detaylı kullanım senaryosu]
    
    ## 🏗️ Teknik Mimari ve Teknoloji Yığını
    
    ### Önerilen Teknolojiler:
    
    #### Frontend:
    - **Ana Teknoloji:** [Teknoloji adı]
    - **Neden bu teknoloji:** [Detaylı açıklama]
    - **Alternatifler:** [Diğer seçenekler]
    
    #### Backend:
    - **Ana Teknoloji:** [Teknoloji adı]
    - **Neden bu teknoloji:** [Detaylı açıklama]
    - **Alternatifler:** [Diğer seçenekler]
    
    #### Veritabanı:
    - **Ana Teknoloji:** [Teknoloji adı]
    - **Neden bu teknoloji:** [Detaylı açıklama]
    - **Veri modeli:** [Temel veri yapısı]
    
    #### Ek Araçlar ve Servisler:
    - **Geliştirme Araçları:** [IDE, Version Control, vb.]
    - **Dağıtım:** [Hosting, CI/CD]
    - **Monitoring:** [Analitik, hata takibi]
    
    ## 📋 Özellik Listesi ve Fonksiyonel Gereksinimler
    
    ### Temel Özellikler (MVP):
    1. **[Özellik 1]**
       - Açıklama: [Detaylı açıklama]
       - Teknik gereksinimler: [Teknik detaylar]
       - Kabul kriterleri: [Test edilebilir kriterler]
    
    2. **[Özellik 2]**
       - Açıklama: [Detaylı açıklama]
       - Teknik gereksinimler: [Teknik detaylar]
       - Kabul kriterleri: [Test edilebilir kriterler]
    
    ### Gelişmiş Özellikler:
    1. **[Gelişmiş Özellik 1]**
       - Açıklama: [Detaylı açıklama]
       - Önkoşullar: [Hangi temel özellikler gerekli]
    
    ## 🗓️ Detaylı Geliştirme Yol Haritası
    
    ### Faz 1: Planlama ve Kurulum ({timeline//4} hafta)
    **Hafta 1-{timeline//4}:**
    - [ ] Proje kurulumu ve geliştirme ortamı hazırlama
    - [ ] Teknik araştırma ve teknoloji seçimi
    - [ ] Proje yapısı ve mimari tasarımı
    - [ ] Veritabanı tasarımı ve modelleme
    - [ ] UI/UX wireframe ve mockup'lar
    
    **Teslim Edilecekler:**
    - Proje kurulum dokümantasyonu
    - Teknik spesifikasyon dökümanı
    - Veritabanı şeması
    - UI mockup'ları
    
    ### Faz 2: Temel Geliştirme ({timeline//2} hafta)
    **Hafta {timeline//4 + 1}-{timeline//2 + timeline//4}:**
    - [ ] Backend API geliştirme
    - [ ] Veritabanı entegrasyonu
    - [ ] Temel frontend arayüzü
    - [ ] Kullanıcı kimlik doğrulama sistemi
    - [ ] Temel CRUD operasyonları
    
    **Teslim Edilecekler:**
    - Çalışan MVP versiyonu
    - API dokümantasyonu
    - Temel test senaryoları
    
    ### Faz 3: Özellik Geliştirme ({timeline//4} hafta)
    **Hafta {timeline//2 + timeline//4 + 1}-{timeline - timeline//4}:**
    - [ ] İleri seviye özellikler
    - [ ] Kullanıcı deneyimi iyileştirmeleri
    - [ ] Performans optimizasyonları
    - [ ] Güvenlik testleri
    - [ ] Responsive tasarım
    
    **Teslim Edilecekler:**
    - Tam özellikli uygulama
    - Performans test raporları
    - Güvenlik analizi
    
    ### Faz 4: Test ve Dağıtım ({timeline//4} hafta)
    **Hafta {timeline - timeline//4 + 1}-{timeline}:**
    - [ ] Kapsamlı test senaryoları
    - [ ] Bug düzeltmeleri
    - [ ] Deployment hazırlığı
    - [ ] Dokümantasyon tamamlama
    - [ ] Kullanıcı kılavuzu hazırlama
    
    **Teslim Edilecekler:**
    - Production-ready uygulama
    - Tam dokümantasyon
    - Kullanıcı kılavuzu
    - Sunum materyalleri
    
    ## 📚 Kapsamlı Öğrenme Kaynakları
    
    ### Temel Kavramlar:
    - **[Teknoloji 1] için kaynaklar:**
      - Resmi dokümantasyon: [Link]
      - Önerilen kurslar: [Kurs isimleri]
      - Pratik projeler: [Örnek projeler]
    
    ### İleri Seviye Konular:
    - **Mimari ve Tasarım:**
      - Clean Architecture
      - Design Patterns
      - SOLID Principles
    
    ### Pratik Kaynaklar:
    - GitHub repositories: [Örnek projeler]
    - YouTube channels: [Önerilen kanallar]
    - Blog posts: [Yararlı blog yazıları]
    - Books: [Önerilen kitaplar]
    
    ## ⚠️ Potansiyel Zorluklar ve Çözümler
    
    ### Teknik Zorluklar:
    1. **[Zorluk 1]**
       - Problem: [Detaylı açıklama]
       - Çözüm: [Önerilen çözüm]
       - Alternatif: [Plan B]
    
    ### Zaman Yönetimi:
    - **Risk:** [Potansiyel gecikme nedeni]
    - **Önlem:** [Önleyici tedbirler]
    
    ## 🎯 Başarı Metrikleri ve Değerlendirme
    
    ### Teknik Metrikler:
    - [ ] Kod kalitesi (Code coverage, linting)
    - [ ] Performans (Yükleme süresi, response time)
    - [ ] Güvenlik (Vulnerability scanning)
    
    ### Kullanıcı Deneyimi:
    - [ ] Kullanılabilirlik testleri
    - [ ] Kullanıcı geri bildirimleri
    - [ ] Erişilebilirlik standartları
    
    ## 🚀 Gelecek Geliştirmeler ve Sürüm Planı
    
    ### Versiyon 2.0 Özellikler:
    - [Gelecek özellik 1]
    - [Gelecek özellik 2]
    
    ### Ölçeklenebilirlik:
    - [Büyüme planı]
    - [Teknik iyileştirmeler]
    
    ## 💡 Bonus İpuçları ve Öneriler
    
    ### Geliştirme Sürecinde:
    - Git kullanımı ve branch stratejisi
    - Code review süreci
    - Continuous Integration/Deployment
    
    ### Portfolyo için:
    - Demo video hazırlama
    - GitHub README optimizasyonu
    - LinkedIn paylaşım stratejisi
    
    ---
    
    **Not:** Bu proje rehberi, {difficulty} seviyesindeki bir öğrenci için {timeline} haftalık sürede tamamlanabilecek şekilde tasarlanmıştır. Her faz sonunda ara değerlendirmeler yaparak ilerlemeyi takip etmeniz önerilir.
    
    **Önemli:** Proje geliştirme sürecinde karşılaştığınız sorunlar için Stack Overflow, GitHub Issues ve ilgili topluluk forumlarını aktif olarak kullanın. Mentorship ve code review için deneyimli geliştiricilerden destek almayı ihmal etmeyin.
    """
    
    return prompt

def create_chat_prompt(message: str, project_context: str = None) -> str:
    """
    Create a comprehensive prompt for chat interactions.
    
    Args:
        message (str): User's chat message
        project_context (str, optional): Context from previously generated project
        
    Returns:
        str: Formatted prompt for chat
    """
    if project_context:
        prompt = f"""
        Sen deneyimli bir yazılım geliştirme mentoru ve proje danışmanısın. 15+ yıl endüstri deneyimin var ve öğrencilere teknik konularda rehberlik etme konusunda uzmansın.
        
        ## Proje Bağlamı:
        Daha önce aşağıdaki detaylı proje rehberini oluşturdun:
        
        {project_context}
        
        ## Öğrenci Sorusu:
        "{message}"
        
        ## Yanıt Formatı ve Beklentiler:
        
        Bu soruyu Türkçe olarak, yukarıdaki proje bağlamında yanıtla. Yanıtın şu kriterleri karşılamalı:
        
        ### 1. Kapsamlı ve Detaylı Olmalı:
        - Sadece kısa cevaplar verme, konuyu derinlemesine açıkla
        - Örnekler ve kod snippet'leri ekle (gerektiğinde)
        - Alternatif yaklaşımları da belirt
        
        ### 2. Pratik ve Uygulanabilir Olmalı:
        - Adım adım talimatlar ver
        - Hangi araçları kullanacağını belirt
        - Potansiyel sorunları ve çözümlerini açıkla
        
        ### 3. Eğitici Olmalı:
        - Neden bu yaklaşımı önerdiğini açıkla
        - İlgili kavramları ve terminolojiyi öğret
        - Ek öğrenme kaynakları öner
        
        ### 4. Motivasyonel Olmalı:
        - Olumlu ve destekleyici bir ton kullan
        - Öğrencinin başarabileceğine dair güven ver
        - Zorluklarla karşılaştığında nasıl üstesinden gelebileceğini açıkla
        
        ### 5. Yapılandırılmış Olmalı:
        - Başlıklar ve alt başlıklar kullan
        - Madde işaretleri ve numaralı listeler kullan
        - Önemli noktaları vurgula
        
        Teknik terimler için gerektiğinde İngilizce karşılıklarını parantez içinde belirt. Yanıtının sonuna ilgili ek sorular öner ki öğrenci daha fazla bilgi alabilsin.
        
        **Önemli:** Yanıtın minimum 200 kelime olmalı ve konuyu gerçekten derinlemesine ele almalı. Yüzeysel cevaplar verme.
        """
    else:
        prompt = f"""
        Sen deneyimli bir yazılım geliştirme mentoru ve proje danışmanısın. 15+ yıl endüstri deneyimin var ve öğrencilere teknik konularda rehberlik etme konusunda uzmansın.
        
        ## Öğrenci Sorusu:
        "{message}"
        
        ## Yanıt Formatı ve Beklentiler:
        
        Bu soruyu Türkçe olarak yanıtla. Yanıtın şu kriterleri karşılamalı:
        
        ### 1. Kapsamlı ve Detaylı Olmalı:
        - Sadece kısa cevaplar verme, konuyu derinlemesine açıkla
        - Örnekler ve kod snippet'leri ekle (gerektiğinde)
        - Farklı yaklaşımları ve seçenekleri belirt
        
        ### 2. Pratik ve Uygulanabilir Olmalı:
        - Adım adım talimatlar ver
        - Hangi araçları ve teknolojileri kullanacağını belirt
        - Başlangıç seviyesinden ileri seviyeye kadar rehberlik et
        
        ### 3. Eğitici Olmalı:
        - Temel kavramları açıkla
        - Neden bu yaklaşımları önerdiğini belirt
        - İlgili terminolojiyi öğret
        - Ek öğrenme kaynakları öner
        
        ### 4. Motivasyonel Olmalı:
        - Olumlu ve destekleyici bir ton kullan
        - Öğrencinin başarabileceğine dair güven ver
        - Karmaşık konuları basit adımlara böl
        
        ### 5. Yapılandırılmış Olmalı:
        - Başlıklar ve alt başlıklar kullan
        - Madde işaretleri ve numaralı listeler kullan
        - Önemli noktaları **kalın** yazı ile vurgula
        
        ### 6. Proje Odaklı Olmalı:
        - Eğer mümkünse, proje fikirleri öner
        - Gerçek dünya uygulamalarına örnekler ver
        - Portfolyo geliştirme önerileri sun
        
        Teknik terimler için gerektiğinde İngilizce karşılıklarını parantez içinde belirt. Yanıtının sonuna öğrencinin daha fazla bilgi alabileceği ilgili sorular öner.
        
        **Önemli:** Yanıtın minimum 250 kelime olmalı ve konuyu gerçekten derinlemesine ele almalı. Yüzeysel cevaplar verme, her zaman detaylı ve öğretici ol.
        """
    
    return prompt

def save_project(project_data: Dict[str, Any], file_path: str = "saved_projects.json") -> bool:
    """
    Save project data to a JSON file.
    
    Args:
        project_data (Dict[str, Any]): Project data to save
        file_path (str, optional): Path to save the file
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Add timestamp
        project_data["timestamp"] = datetime.now().isoformat()
        
        # Load existing projects if file exists
        existing_projects = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_projects = json.load(f)
        
        # Append new project
        existing_projects.append(project_data)
        
        # Save back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_projects, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        return False

def load_saved_projects(file_path: str = "saved_projects.json") -> List[Dict[str, Any]]:
    """
    Load saved projects from a JSON file.
    
    Args:
        file_path (str, optional): Path to the JSON file
        
    Returns:
        List[Dict[str, Any]]: List of saved projects
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading saved projects: {e}")
        return []

def export_to_markdown(project_data: Dict[str, Any], file_path: str = None) -> Optional[str]:
    """
    Export project data to a Markdown file.
    
    Args:
        project_data (Dict[str, Any]): Project data to export
        file_path (str, optional): Path to save the file
        
    Returns:
        Optional[str]: Path to the saved file or None if failed
    """
    try:
        content = project_data.get("content", "")
        title = project_data.get("title", "Proje Önerisi")
        
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{title.replace(' ', '_')}_{timestamp}.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    except Exception as e:
        logger.error(f"Error exporting to markdown: {e}")
        return None

def export_to_pdf(project_data: Dict[str, Any], file_path: str = None) -> Optional[str]:
    """
    Export project data to a PDF file.
    
    Args:
        project_data (Dict[str, Any]): Project data to export
        file_path (str, optional): Path to save the file
        
    Returns:
        Optional[str]: Path to the saved file or None if failed
    """
    try:
        # This is a placeholder - in a real implementation, you would use a PDF library
        # such as reportlab, fpdf, or weasyprint to convert the content to PDF
        content = project_data.get("content", "")
        title = project_data.get("title", "Proje Önerisi")
        
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"{title.replace(' ', '_')}_{timestamp}.pdf"
        
        # Placeholder for PDF generation
        # For now, just save as markdown
        return export_to_markdown(project_data, file_path.replace('.pdf', '.md'))
    except Exception as e:
        logger.error(f"Error exporting to PDF: {e}")
        return None

def extract_title_from_content(content: str) -> str:
    """
    Extract the project title from the generated content.
    
    Args:
        content (str): Generated project content
        
    Returns:
        str: Extracted title or default title
    """
    try:
        # Look for a title in the format "### 1. Proje Başlığı" followed by text
        import re
        title_match = re.search(r'#+\s*1\.\s*Proje\s*Başlığı\s*\n+([^\n#]+)', content)
        if title_match:
            return title_match.group(1).strip()
        
        # Alternative: look for the first heading
        heading_match = re.search(r'#+\s*([^\n#]+)', content)
        if heading_match:
            return heading_match.group(1).strip()
        
        return "Proje Önerisi"
    except Exception as e:
        logger.error(f"Error extracting title: {e}")
        return "Proje Önerisi"

def get_download_link(content: str, filename: str, text: str) -> str:
    """
    Generate a download link for a string content.
    
    Args:
        content (str): Content to download
        filename (str): Name of the file to download
        text (str): Text to display for the download link
        
    Returns:
        str: HTML string with the download link
    """
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def apply_custom_css() -> None:
    """Apply custom CSS to the Streamlit app."""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #E3F2FD;
        padding-bottom: 0.3rem;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #43A047;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #FFA000;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #E53935;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
    }
    .stButton>button:focus {
        outline: none;
        box-shadow: 0 0 0 2px rgba(30, 136, 229, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

def display_info_box(text: str) -> None:
    """Display an info box with custom styling."""
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)

def display_success_box(text: str) -> None:
    """Display a success box with custom styling."""
    st.markdown(f'<div class="success-box">{text}</div>', unsafe_allow_html=True)

def display_warning_box(text: str) -> None:
    """Display a warning box with custom styling."""
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)

def display_error_box(text: str) -> None:
    """Display an error box with custom styling."""
    st.markdown(f'<div class="error-box">{text}</div>', unsafe_allow_html=True) 