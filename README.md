# 🎓 AI Project Generator - Öğrenci Proje Fikri Üretici

## 📋 Proje Hakkında

Bu proje, **Clean Code (Temiz Kod) prensiplerini** öğrencilere öğretmek amacıyla geliştirilmiş bir **Streamlit** uygulamasıdır. Gemini AI kullanarak öğrenciler için kişiselleştirilmiş proje fikirleri üretir ve detaylı uygulama rehberleri sunar.

### 🎯 Eğitim Hedefleri

Bu proje aşağıdaki **Clean Code prensiplerini** gösterir:
- ✅ **Magic String ve Number'ların eliminasyonu**
- ✅ **Constants dosyası kullanımı**
- ✅ **Single Responsibility Principle (SRP)**
- ✅ **Clear naming conventions**
- ✅ **Proper error handling**
- ✅ **Modular architecture**
- ✅ **Type annotations**
- ✅ **Comprehensive documentation**

## 🏗️ Proje Mimarisi

```
AIFD-V1/
├── 📁 config/
│   ├── __init__.py
│   ├── settings.py          # Uygulama ayarları
│   └── constants.py         # 🔑 TÜM magic string/number'lar burada!
├── 📁 components/
│   ├── __init__.py
│   ├── input_forms.py       # Form bileşenleri
│   ├── project_generator.py # Proje üretim logic'i
│   └── chat_interface.py    # Sohbet arayüzü
├── 📁 utils/
│   ├── __init__.py
│   ├── gemini_client.py     # AI client
│   └── helpers.py           # Yardımcı fonksiyonlar
├── main.py                  # Ana uygulama dosyası
├── app.py                   # Backward compatibility
├── requirements.txt         # Gerekli paketler
└── README.md               # Bu dosya
```

## 🔑 Clean Code Örnekleri

### ❌ KÖTÜ ÖRNEK (Magic Strings)
```python
# YAPMAYIN!
if st.button("💾 Projeyi Kaydet"):
    st.success("Proje başarıyla kaydedildi!")
    
temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
```

### ✅ İYİ ÖRNEK (Constants Kullanımı)
```python
# YAPINIZ!
from config.constants import SAVE_PROJECT_BUTTON, SUCCESS_PROJECT_SAVED
from config.constants import TEMPERATURE_MIN, TEMPERATURE_MAX, TEMPERATURE_DEFAULT

if st.button(SAVE_PROJECT_BUTTON):
    st.success(SUCCESS_PROJECT_SAVED)
    
temperature = st.slider(
    TEMPERATURE_LABEL,
    min_value=TEMPERATURE_MIN,
    max_value=TEMPERATURE_MAX,
    value=TEMPERATURE_DEFAULT,
    step=TEMPERATURE_STEP
)
```

### 🎯 Single Responsibility Principle Örneği

```python
# ❌ KÖTÜ: Tek fonksiyon çok şey yapıyor
def handle_everything(user_inputs, model_config):
    # Input validation
    # Image processing  
    # AI call
    # Response processing
    # UI updates
    # Error handling
    pass

# ✅ İYİ: Her fonksiyon tek sorumluluğa sahip
def _validate_user_inputs(user_inputs: dict) -> bool:
    """Sadece input validasyonu yapar"""
    
def _process_image_input(user_inputs: dict) -> Optional[Image.Image]:
    """Sadece image işleme yapar"""
    
def _generate_ai_response(client, prompt, config, image) -> str:
    """Sadece AI response üretir"""
```

## 🚀 Kurulum ve Çalıştırma

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Çevre Değişkenleri
`.env` dosyası oluşturun:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Uygulamayı Çalıştırın
```bash
streamlit run main.py
```

## 📚 Öğrenme Kaynakları

### Clean Code Prensipleri
1. **[Clean Code Book - Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350884)**
2. **[SOLID Principles](https://en.wikipedia.org/wiki/SOLID)**
3. **[Python PEP 8 Style Guide](https://pep8.org/)**

### Python Best Practices
1. **[Type Hints](https://docs.python.org/3/library/typing.html)**
2. **[Docstring Conventions](https://pep257.readthedocs.io/)**
3. **[Error Handling](https://docs.python.org/3/tutorial/errors.html)**

## 🔧 Teknoloji Yığını

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini API
- **Language**: Python 3.8+
- **Architecture**: Modular MVC Pattern

## 📖 Kod İnceleme Rehberi

### 1. Constants Dosyası (`config/constants.py`)
```python
# ✅ Tüm magic string'ler burada tanımlı
PAGE_TITLE = "Öğrenci Proje Fikri Üretici"
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 1.0
STATUS_GENERATING = "🚀 Proje fikirleri oluşturuluyor..."
```

### 2. Modular Functions (`components/`)
Her component tek sorumluluğa sahip:
- `input_forms.py` → Sadece form UI'ları
- `project_generator.py` → Sadece proje üretimi
- `chat_interface.py` → Sadece chat functionality

### 3. Error Handling
```python
try:
    response = client.generate_project_ideas(...)
except Exception as e:
    logger.error(f"Error generating project ideas: {e}")
    return False, error_message, None
```

### 4. Type Annotations
```python
def generate_project_ideas(
    user_inputs: Dict[str, Any], 
    model_config: Dict[str, Any]
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
```

## 🎯 Öğrenciler İçin Alıştırmalar

### Başlangıç Seviyesi
1. `constants.py` dosyasına yeni bir constant ekleyin
2. Bir fonksiyona type annotation ekleyin
3. Bir magic string'i constant ile değiştirin

### Orta Seviye
1. Yeni bir component oluşturun
2. Error handling ekleyin
3. Private function (`_function_name`) oluşturun

### İleri Seviye
1. Yeni bir design pattern uygulayın
2. Unit test yazın
3. Performance optimization yapın

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Clean code prensiplerini takip edin
4. Commit yapın (`git commit -m 'Add amazing feature'`)
5. Push yapın (`git push origin feature/amazing-feature`)
6. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 👥 Katkıda Bulunanlar

- **AI Project Generator Team** - *Initial work*

## 📞 İletişim

Sorularınız için:
- 📧 Email: [your-email@example.com]
- 💬 Issues: GitHub Issues bölümünü kullanın

---

## 🎓 Eğitim Notları

### Bu projeyi incelerken dikkat edilmesi gerekenler:

1. **Constants Kullanımı**: Her magic string/number `constants.py`'da tanımlı
2. **Function Naming**: Fonksiyon isimleri ne yaptığını açık şekilde belirtiyor
3. **Single Responsibility**: Her fonksiyon tek bir şey yapıyor
4. **Error Handling**: Her olası hata durumu ele alınmış
5. **Documentation**: Her fonksiyon detaylı olarak dokümante edilmiş
6. **Type Safety**: Type annotations kullanılmış
7. **Modular Design**: Kod mantıklı modüllere ayrılmış

### 💡 Pro Tips:
- Kod yazmadan önce `constants.py`'ı inceleyin
- Yeni özellik eklerken önce constants ekleyin
- Her zaman type annotations kullanın
- Private functions için `_` prefix kullanın
- Error handling'i unutmayın
