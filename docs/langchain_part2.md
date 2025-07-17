# LangChain ve RAG Ekosistemi - Bölüm 2: LangChain Detayları

## 🔗 Chain'ler (Zincirler) - Derinlemesine

### Chain Nedir?
Chain'leri **fabrika üretim hattı** olarak düşünün. Her istasyon (chain) belirli bir işlemi yapar ve sonucu bir sonraki istasyona geçirir.

```
Ham Malzeme → [İşlem 1] → [İşlem 2] → [İşlem 3] → Final Ürün
    ↓              ↓          ↓          ↓         ↓
  Soru    →   [Analiz] → [Araştır] → [Sentez] → Cevap
```

### 1. **LLMChain - Temel Yapı Taşı**
```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI

# Basit bir chain
llm = OpenAI(temperature=0.7)
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Aşağıdaki konu hakkında 3 madde yazın: {topic}"
)

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("Python programlama")
print(result)
```

### 2. **SimpleSequentialChain - Sıralı İşlemler**
```python
from langchain.chains import SimpleSequentialChain

# İlk chain: Konu analizi
analysis_prompt = PromptTemplate(
    input_variables=["topic"],
    template="Bu konunun ana başlıklarını listele: {topic}"
)
analysis_chain = LLMChain(llm=llm, prompt=analysis_prompt)

# İkinci chain: Detaylı açıklama
detail_prompt = PromptTemplate(
    input_variables=["outline"],
    template="Bu ana başlıkları detaylandır: {outline}"
)
detail_chain = LLMChain(llm=llm, prompt=detail_prompt)

# Zincirleri birleştir
overall_chain = SimpleSequentialChain(
    chains=[analysis_chain, detail_chain],
    verbose=True
)

# Kullanım
result = overall_chain.run("Makine öğrenmesi")
```

### 3. **SequentialChain - Karmaşık İş Akışları**
```python
from langchain.chains import SequentialChain

# Çoklu input/output chain
# 1. Ürün analizi
product_analysis = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["product_name"],
        template="Bu ürünün teknik özelliklerini analiz et: {product_name}"
    ),
    output_key="technical_specs"
)

# 2. Pazar araştırması
market_research = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["product_name"],
        template="Bu ürün için pazar analizi yap: {product_name}"
    ),
    output_key="market_analysis"
)

# 3. Fiyat önerisi
pricing_strategy = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["technical_specs", "market_analysis"],
        template="""
        Teknik özellikler: {technical_specs}
        Pazar analizi: {market_analysis}
        
        Bu bilgilere dayanarak fiyat stratejisi öner:
        """
    ),
    output_key="pricing_strategy"
)

# Tüm zincirleri birleştir
product_chain = SequentialChain(
    chains=[product_analysis, market_research, pricing_strategy],
    input_variables=["product_name"],
    output_variables=["technical_specs", "market_analysis", "pricing_strategy"],
    verbose=True
)

# Kullanım
result = product_chain({
    "product_name": "Akıllı Saat"
})

print("Teknik Özellikler:", result["technical_specs"])
print("Pazar Analizi:", result["market_analysis"])
print("Fiyat Stratejisi:", result["pricing_strategy"])
```

### 4. **ConversationChain - Hafızalı Sohbet**
```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Hafıza ile sohbet
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Konuşma
print(conversation.predict(input="Merhaba, adım Ali"))
print(conversation.predict(input="Python öğreniyorum"))
print(conversation.predict(input="Adımı hatırlıyor musun?"))
```

---

## 🧠 Memory Sistemleri - Derinlemesine

### Memory Türleri

#### 1. **ConversationBufferMemory - Basit Hafıza**
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()

# Manuel olarak hafızaya ekle
memory.save_context(
    {"input": "Python nedir?"},
    {"output": "Python bir programlama dilidir..."}
)

# Hafızayı görüntüle
print(memory.buffer)
```

#### 2. **ConversationBufferWindowMemory - Pencere Hafıza**
```python
from langchain.memory import ConversationBufferWindowMemory

# Sadece son 2 konuşmayı hatırla
window_memory = ConversationBufferWindowMemory(k=2)

# Birden fazla konuşma ekle
conversations = [
    ("Merhaba", "Merhaba! Nasıl yardımcı olabilirim?"),
    ("Python öğreniyorum", "Harika! Hangi konuda yardım istiyorsun?"),
    ("Döngüler nasıl çalışır", "Python'da for ve while döngüleri vardır..."),
    ("Örnekle göster", "Tabii, işte bir örnek...")
]

for inp, out in conversations:
    window_memory.save_context({"input": inp}, {"output": out})

print("Hafızada kalan:", window_memory.buffer)
```

#### 3. **ConversationSummaryMemory - Özet Hafıza**
```python
from langchain.memory import ConversationSummaryMemory

# Uzun konuşmaları özetler
summary_memory = ConversationSummaryMemory(llm=llm)

# Uzun bir konuşma simülasyonu
long_conversation = """
Human: Python öğrenmeye yeni başladım. Nereden başlamalıyım?
AI: Python öğrenmeye başlamak için önce temel syntax'ı öğrenmelisin. Değişkenler, veri tipleri, koşullar ve döngüler ile başla.
Human: Değişken nedir?
AI: Değişken, verileri saklamak için kullanılan isimlendirilmiş konteynerlerdir. Python'da değişken tanımlamak için sadece isim = değer yazmanız yeterlidir.
Human: Peki veri tipleri nelerdir?
AI: Python'da ana veri tipleri şunlardır: int (tam sayı), float (ondalık sayı), str (metin), bool (doğru/yanlış), list (liste), dict (sözlük).
"""

# Özet oluştur
summary_memory.save_context(
    {"input": "Python öğrenme konuşması"},
    {"output": long_conversation}
)

print("Konuşma özeti:", summary_memory.buffer)
```

#### 4. **ConversationSummaryBufferMemory - Hibrit Hafıza**
```python
from langchain.memory import ConversationSummaryBufferMemory

# Hem son konuşmaları hem de özetleri saklar
hybrid_memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=100,  # Token limiti
    return_messages=True
)

# Kullanım
conversation_with_hybrid = ConversationChain(
    llm=llm,
    memory=hybrid_memory,
    verbose=True
)
```

### 5. **VectorStoreRetrieverMemory - Vektör Hafıza**
```python
from langchain.memory import VectorStoreRetrieverMemory
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

# Vektör tabanlı hafıza
vectorstore = Chroma(embedding_function=OpenAIEmbeddings())
retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))

vector_memory = VectorStoreRetrieverMemory(retriever=retriever)

# Hafızaya kaydet
vector_memory.save_context(
    {"input": "Favori rengim mavi"},
    {"output": "Anladım, favori renginiz mavi."}
)

vector_memory.save_context(
    {"input": "Köpeğim var"},
    {"output": "Harika! Köpeğinizin adı nedir?"}
)

# İlgili hatıraları getir
relevant_memories = vector_memory.load_memory_variables(
    {"prompt": "Hangi hayvan seviyorum?"}
)
print(relevant_memories)
```

---

## 🤖 Agent'lar - Akıllı Asistanlar

### Agent Nedir?
Agent'ları **problem çözen robot** olarak düşünün. Kendilerine verilen araçları kullanarak karmaşık görevleri yerine getirirler.

### Agent Türleri

#### 1. **Zero-shot ReAct Agent**
```python
from langchain.agents import initialize_agent, AgentType
from langchain.agents import load_tools
from langchain.llms import OpenAI

# LLM başlat
llm = OpenAI(temperature=0)

# Araçları yükle
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# Agent oluştur
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Kullanım
result = agent.run("2024 yılında Türkiye'nin nüfusu kaç? Bu sayının karesini al.")
```

#### 2. **Conversational Agent**
```python
from langchain.memory import ConversationBufferMemory

# Hafızalı agent
memory = ConversationBufferMemory(memory_key="chat_history")

conversational_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory
)

# Sıralı sorular
print(conversational_agent.run("Merhaba, adım Ahmet"))
print(conversational_agent.run("Python ile matematik işlemi yapmak istiyorum"))
print(conversational_agent.run("25 x 34 nedir?"))
print(conversational_agent.run("Adımı hatırlıyor musun?"))
```

### 3. **Custom Tools - Özel Araçlar**
```python
from langchain.tools import BaseTool
from typing import Optional
import requests

class WeatherTool(BaseTool):
    name = "hava_durumu"
    description = "Belirtilen şehrin hava durumunu getirir"
    
    def _run(self, city: str) -> str:
        """Hava durumu API'sini çağır"""
        # Örnek API çağrısı (gerçek API key gerekir)
        api_key = "your_weather_api_key"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=tr"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                return f"{city} şehrinde hava durumu: {description}, sıcaklık: {temp}°C"
            else:
                return f"Hava durumu bilgisi alınamadı: {data.get('message', 'Bilinmeyen hata')}"
                
        except Exception as e:
            return f"Hata oluştu: {str(e)}"
    
    async def _arun(self, city: str) -> str:
        """Async version"""
        raise NotImplementedError("Bu araç async çalışmayı desteklemiyor")

class DatabaseTool(BaseTool):
    name = "veritabani_sorgula"
    description = "Şirket veritabanından bilgi getirir"
    
    def _run(self, query: str) -> str:
        """Veritabanı sorgusu simülasyonu"""
        # Gerçek uygulamada burada veritabanı bağlantısı olur
        fake_db = {
            "çalışan sayısı": "Şirketimizde toplam 150 çalışan bulunmaktadır",
            "departmanlar": "IT, İnsan Kaynakları, Pazarlama, Satış, Finans departmanlarımız var",
            "ofis konumu": "Ana ofisimiz İstanbul Levent'te, şube ofisimiz Ankara'da bulunmaktadır"
        }
        
        for key, value in fake_db.items():
            if key.lower() in query.lower():
                return value
        
        return "Bu konuda bilgi bulunamadı"
    
    async def _arun(self, query: str) -> str:
        raise NotImplementedError()

# Özel araçları kullan
custom_tools = [WeatherTool(), DatabaseTool()]

custom_agent = initialize_agent(
    custom_tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Test
result = custom_agent.run("Şirketimizde kaç çalışan var ve İstanbul'da hava nasıl?")
```

### 4. **Plan-and-Execute Agent**
```python
from langchain.experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner

# Planlayıcı ve yürütücü oluştur
model = OpenAI(temperature=0)
planner = load_chat_planner(model)
executor = load_agent_executor(model, tools, verbose=True)

# Plan-and-Execute agent
plan_execute_agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

# Karmaşık görev
complex_task = """
Türkiye'nin 2024 yılı ekonomik verilerini araştır ve aşağıdaki soruları cevapla:
1. GDP büyüme oranı nedir?
2. İşsizlik oranı kaç?
3. Enflasyon oranı nedir?
4. Bu verilere göre genel ekonomik durumu değerlendir
"""

result = plan_execute_agent.run(complex_task)
```

---

## 🔧 Tools (Araçlar) - Detaylı İnceleme

### Built-in Tools

#### 1. **SerpAPI - Web Arama**
```python
from langchain.utilities import SerpAPIWrapper

search = SerpAPIWrapper()
result = search.run("LangChain nedir 2024")
print(result)
```

#### 2. **Calculator - Matematik İşlemleri**
```python
from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import WolframAlphaAPIWrapper

# Wolfram Alpha hesap makinesi
wolfram = WolframAlphaAPIWrapper()
math_result = wolfram.run("(25 + 34) * 2 / 3")
print(math_result)
```

#### 3. **Wikipedia Tool**
```python
from langchain.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
wiki_result = wikipedia.run("Python programlama dili")
print(wiki_result)
```

### Custom API Tools
```python
from langchain.tools import APIOperation, OpenAPISpec
from langchain.requests import RequestsWrapper

# OpenAPI spec'ten araç oluşturma
spec = OpenAPISpec.from_url("https://jsonplaceholder.typicode.com/")
operation = APIOperation.from_openapi_spec(spec, "/posts", "get")

# Requests wrapper
requests_wrapper = RequestsWrapper()

# API aracını kullan
api_tool = operation.to_tool(requests_wrapper)
```

### File System Tools
```python
from langchain.tools.file_management import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool
)

# Dosya işlemleri araçları
read_tool = ReadFileTool()
write_tool = WriteFileTool()
list_tool = ListDirectoryTool()

file_tools = [read_tool, write_tool, list_tool]

# Dosya yöneticisi agent
file_agent = initialize_agent(
    file_tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Kullanım
file_agent.run("belgeler klasöründeki dosyaları listele ve README.md dosyasını oku")
```

---

## 🔄 Callbacks - Olay İzleme

### Callback Sistemini Anlamak
Callback'ler, LangChain işlemlerini **canlı takip etme** yöntemidir.

```python
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from typing import Dict, Any

class CustomCallbackHandler(BaseCallbackHandler):
    """Özel callback handler"""
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list, **kwargs) -> None:
        print(f"🚀 LLM başladı. Prompt sayısı: {len(prompts)}")
    
    def on_llm_end(self, response, **kwargs) -> None:
        print("✅ LLM tamamlandı")
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        print(f"❌ LLM hatası: {error}")
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        print(f"🔗 Chain başladı: {serialized.get('name', 'Bilinmeyen')}")
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        print("✅ Chain tamamlandı")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        print(f"🛠️ Tool kullanılıyor: {serialized.get('name')} - Input: {input_str}")
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        print(f"✅ Tool tamamlandı - Output: {output[:100]}...")

# Callback'i kullan
custom_handler = CustomCallbackHandler()

chain_with_callback = LLMChain(
    llm=llm,
    prompt=prompt,
    callbacks=[custom_handler]
)

result = chain_with_callback.run("Python nedir?")
```

### Token Tracking Callback
```python
from langchain.callbacks import get_openai_callback

# Token ve maliyet takibi
with get_openai_callback() as cb:
    result = chain.run("Uzun bir makale yaz")
    
    print(f"Toplam token: {cb.total_tokens}")
    print(f"Prompt token: {cb.prompt_tokens}")
    print(f"Completion token: {cb.completion_tokens}")
    print(f"Toplam maliyet: ${cb.total_cost}")
```

---

## 📊 Output Parsers - Çıktı İşlemcileri

### Structured Output
```python
from langchain.output_parsers import PydanticOutputParser, CommaSeparatedListOutputParser
from langchain.schema import OutputParserException
from pydantic import BaseModel, Field
from typing import List

# Pydantic model tanımla
class ProductAnalysis(BaseModel):
    product_name: str = Field(description="ürün adı")
    category: str = Field(description="ürün kategorisi")
    price_range: str = Field(description="fiyat aralığı")
    pros: List[str] = Field(description="artıları")
    cons: List[str] = Field(description="eksileri")
    rating: int = Field(description="1-10 arası puan")

# Parser oluştur
parser = PydanticOutputParser(pydantic_object=ProductAnalysis)

# Prompt template'e format talimatı ekle
prompt_template = PromptTemplate(
    template="Aşağıdaki ürünü analiz et ve JSON formatında döndür.\n{format_instructions}\n\nÜrün: {product}\n",
    input_variables=["product"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Chain oluştur
analysis_chain = LLMChain(llm=llm, prompt=prompt_template)

# Kullanım
raw_output = analysis_chain.run("iPhone 15 Pro")
try:
    parsed_output = parser.parse(raw_output)
    print(f"Ürün: {parsed_output.product_name}")
    print(f"Kategori: {parsed_output.category}")
    print(f"Puan: {parsed_output.rating}")
    print(f"Artılar: {parsed_output.pros}")
except OutputParserException as e:
    print(f"Parser hatası: {e}")
```

### List Output Parser
```python
# Liste formatında çıktı
list_parser = CommaSeparatedListOutputParser()

list_prompt = PromptTemplate(
    template="Python öğrenmek için 5 kaynak öner.\n{format_instructions}\n",
    input_variables=[],
    partial_variables={"format_instructions": list_parser.get_format_instructions()}
)

list_chain = LLMChain(llm=llm, prompt=list_prompt)
raw_list = list_chain.run("")
parsed_list = list_parser.parse(raw_list)

print("Önerilen kaynaklar:")
for i, kaynak in enumerate(parsed_list, 1):
    print(f"{i}. {kaynak}")
```

---

## 🎯 Gerçek Hayat Projesi: E-Ticaret Asistanı

```python
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
import json

class ProductSearchTool(BaseTool):
    name = "urun_ara"
    description = "E-ticaret sitesinde ürün arar"
    
    def _run(self, query: str) -> str:
        # Simülasyon verisi
        products = {
            "laptop": [
                {"name": "MacBook Pro", "price": 45000, "stock": 5},
                {"name": "Dell XPS", "price": 35000, "stock": 8},
                {"name": "Lenovo ThinkPad", "price": 28000, "stock": 12}
            ],
            "telefon": [
                {"name": "iPhone 15", "price": 55000, "stock": 3},
                {"name": "Samsung Galaxy", "price": 42000, "stock": 7},
                {"name": "Xiaomi Mi", "price": 18000, "stock": 15}
            ]
        }
        
        for category, items in products.items():
            if category in query.lower():
                return json.dumps(items, ensure_ascii=False, indent=2)
        
        return "Bu kategoride ürün bulunamadı"
    
    async def _arun(self, query: str) -> str:
        raise NotImplementedError()

class OrderStatusTool(BaseTool):
    name = "siparis_durumu"
    description = "Sipariş numarasına göre sipariş durumunu kontrol eder"
    
    def _run(self, order_number: str) -> str:
        # Simülasyon
        orders = {
            "SP001": "Kargoya verildi - Tahmini teslimat: 2 gün",
            "SP002": "Hazırlanıyor - Tahmini kargo: 1 gün",
            "SP003": "Teslim edildi"
        }
        
        return orders.get(order_number, "Sipariş numarası bulunamadı")
    
    async def _arun(self, order_number: str) -> str:
        raise NotImplementedError()

class PriceCompareTool(BaseTool):
    name = "fiyat_karsilastir"
    description = "Ürünlerin fiyatlarını karşılaştırır"
    
    def _run(self, product_name: str) -> str:
        # Simülasyon
        price_data = {
            "iphone": {
                "bizim_site": 55000,
                "rakip1": 57000,
                "rakip2": 54500,
                "ortalama": 55500
            },
            "macbook": {
                "bizim_site": 45000,
                "rakip1": 47000,
                "rakip2": 46000,
                "ortalama": 46000
            }
        }
        
        for product, prices in price_data.items():
            if product in product_name.lower():
                return f"""
                Fiyat Karşılaştırması - {product_name}:
                Bizim site: {prices['bizim_site']} TL
                Rakip 1: {prices['rakip1']} TL
                Rakip 2: {prices['rakip2']} TL
                Piyasa ortalaması: {prices['ortalama']} TL
                
                Bizim fiyatımız piyasa ortalamasından %{((prices['ortalama'] - prices['bizim_site']) / prices['ortalama'] * 100):.1f} daha uygun!
                """
        
        return "Bu ürün için fiyat karşılaştırması bulunamadı"
    
    async def _arun(self, product_name: str) -> str:
        raise NotImplementedError()

# E-ticaret asistanı oluştur
class EticaretAsistani:
    def __init__(self):
        self.llm = OpenAI(temperature=0.2)
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
        # Araçları yükle
        self.tools = [
            ProductSearchTool(),
            OrderStatusTool(),
            PriceCompareTool()
        ]
        
        # Agent oluştur
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    def chat(self, message: str):
        """Müşteri ile sohbet et"""
        return self.agent.run(message)

# Kullanım
asistan = EticaretAsistani()

# Örnek konuşmalar
print("🛒 E-ticaret Asistanı Aktif!")
print("=" * 50)

conversations = [
    "Merhaba, laptop arıyorum",
    "MacBook Pro ile Dell XPS'i karşılaştırır mısın?",
    "MacBook'un fiyatını diğer sitelerle karşılaştır",
    "SP001 numaralı siparişimin durumu nedir?",
    "Telefon kategorisinde ne var?"
]

for conv in conversations:
    print(f"\n👤 Müşteri: {conv}")
    response = asistan.chat(conv)
    print(f"🤖 Asistan: {response}")
    print("-" * 50)
```

---

## 🎯 Bölüm 2 Özeti

Bu bölümde öğrendikleriniz:

### ✅ **Gelişmiş Chain Kullanımı:**
- Sequential Chain'ler ile karmaşık iş akışları
- Memory sistemi ile hafızalı uygulamalar
- Custom Chain'ler oluşturma

### ✅ **Agent Sistemleri:**
- Farklı Agent türlerini anlama
- Custom Tools oluşturma
- Plan-and-Execute pattern

### ✅ **Teknik Detaylar:**
- Callback sistemleri ile monitoring
- Output Parser'lar ile yapılandırılmış çıktı
- Error handling ve optimization

### ✅ **Gerçek Proje:**
- E-ticaret asistanı geliştirme
- Multiple tools entegrasyonu
- Conversational interface

### 🔜 **Sonraki Bölümde:**
- ChromaDB detayları
- Vektör veritabanı optimizasyonu
- Embedding teknikleri
- Similarity search algoritmaları

Bu bölüm ile LangChain'in temel bileşenlerini derinlemesine öğrendiniz. Sonraki bölümde ChromaDB ve vektör veritabanları konusuna odaklanacağız.