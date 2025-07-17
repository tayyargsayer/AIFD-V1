# LangChain ve RAG Ekosistemi - Bölüm 1: Temeller

## İçindekiler - Genel Bakış

### 📚 Dokümantasyon Yapısı:
- **Bölüm 1**: Temeller (LangChain nedir, RAG konsepti)
- **Bölüm 2**: LangChain Detayları (Chain'ler, Agent'lar, Memory)
- **Bölüm 3**: ChromaDB ve Vektör Veritabanları  
- **Bölüm 4**: LangGraph ve Complex Workflows
- **Bölüm 5**: Pratik Projeler ve Entegrasyonlar

---

## 🚀 LangChain Nedir?

### Basit Anlatım
LangChain'i **dijital bir asistan yaratma seti** olarak düşünün. Tıpkı LEGO blokları gibi, farklı AI parçalarını birleştirerek güçlü uygulamalar oluşturursunuz.

### Gerçek Hayat Analojisi: **Şef ve Mutfak**
Bir restoran şefi düşünün:
- **Şef** = LLM (ChatGPT, Claude)
- **Tarifler** = Prompt Templates
- **Malzemeler** = Veri kaynakları
- **Mutfak aletleri** = Tools
- **Servis** = Chains

LangChain, bu tüm elemanları organize eden **mutfak yöneticisi** gibidir.

### Neden LangChain?

#### ❌ **LangChain Olmadan:**
```python
# Karmaşık ve tekrarlayan kod
import openai
import requests
import json

def ask_llm(question):
    # API key yönetimi
    # Prompt formatı
    # Hata yönetimi
    # Token limiti kontrolü
    # ... 50+ satır kod

def search_database(query):
    # Veritabanı bağlantısı
    # Query optimizasyonu
    # Sonuç formatı
    # ... 30+ satır kod

# Her seferinde tekrardan yazıyorsunuz
```

#### ✅ **LangChain İle:**
```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Sadece 3 satırda hazır!
llm = OpenAI()
prompt = PromptTemplate.from_template("Soru: {question}")
chain = LLMChain(llm=llm, prompt=prompt)

result = chain.run("Python nedir?")
```

---

## 🧠 RAG (Retrieval-Augmented Generation) Nedir?

### Basit Anlatım
RAG, AI'nın **hafızasını genişletme** yöntemidir. Sanki AI'ya **kişisel kütüphaneci** veriyorsunuz.

### RAG Analojisi: **Sınav Öncesi Çalışma**
Bir sınava hazırlandığınızı düşünün:

#### 🧠 **Normal AI (Geleneksel LLM)**:
- Sadece aklınızda olan bilgilerle cevap verirsiniz
- Bilmediğiniz bir soru gelirse "bilmiyorum" dersiniz
- Güncel bilgiler yoktur

#### 📚 **RAG ile AI**:
- Soru geldiğinde önce kitaplardan araştırma yaparsınız
- Bulduğunuz bilgileri kullanarak cevap verirsiniz
- Güncel kaynakları kullanabilirsiniz

### RAG Süreci: **3 Adım**

#### 1. **Retrieval (Bilgi Bulma)**
```
Kullanıcı: "2024'te Bitcoin fiyatı ne oldu?"
        ↓
Sistem: Vektör veritabanında araştır
        ↓
Sonuç: İlgili dokümanları bul
```

#### 2. **Augmentation (Bilgi Ekleme)**
```
Bulunan bilgi + Kullanıcı sorusu = Zenginleştirilmiş Prompt
```

#### 3. **Generation (Cevap Üretme)**
```
LLM: Zenginleştirilmiş prompt'u kullanarak cevap üret
```

### RAG Mimarisi

```
[Dökümanlar] → [Chunking] → [Embedding] → [Vektör DB]
                                              ↓
[Kullanıcı Sorusu] → [Embedding] → [Similarity Search]
                                              ↓
[İlgili Dökümanlar] + [Soru] → [LLM] → [Cevap]
```

---

## 🔧 LangChain Ana Bileşenleri

### 1. **LLMs (Large Language Models)**
```python
from langchain.llms import OpenAI, Anthropic, HuggingFacePipeline

# Farklı LLM'leri kullanabilirsiniz
openai_llm = OpenAI(temperature=0.7)
anthropic_llm = Anthropic()
local_llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/DialoGPT-medium",
    task="text-generation"
)
```

### 2. **Prompts (Yönlendirme Şablonları)**
```python
from langchain.prompts import PromptTemplate, FewShotPromptTemplate

# Basit prompt
simple_prompt = PromptTemplate(
    input_variables=["product"],
    template="Aşağıdaki ürün hakkında bir inceleme yazın: {product}"
)

# Few-shot prompt (örneklerle)
examples = [
    {"input": "iPhone", "output": "iPhone, Apple'ın premium akıllı telefonu..."},
    {"input": "Samsung", "output": "Samsung, güçlü Android deneyimi sunan..."}
]

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate(
        input_variables=["input", "output"],
        template="Ürün: {input}\nİnceleme: {output}"
    ),
    prefix="Ürün incelemeleri yazın:",
    suffix="Ürün: {input}\nİnceleme:",
    input_variables=["input"]
)
```

### 3. **Chains (Zincirler)**
```python
from langchain.chains import LLMChain, SimpleSequentialChain

# Basit chain
chain = LLMChain(llm=llm, prompt=prompt)

# Sequential chain (birden fazla adım)
# 1. Adım: Ürün özelliklerini analiz et
analyze_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["product"],
        template="Bu ürünün teknik özelliklerini listele: {product}"
    )
)

# 2. Adım: İnceleme yaz
review_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["features"],
        template="Bu özelliklere dayalı bir inceleme yaz: {features}"
    )
)

# Zincirleri birleştir
overall_chain = SimpleSequentialChain(
    chains=[analyze_chain, review_chain],
    verbose=True
)
```

### 4. **Memory (Hafıza)**
```python
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory

# Basit hafıza (tüm konuşmayı saklar)
memory = ConversationBufferMemory()

# Özet hafıza (uzun konuşmaları özetler)
summary_memory = ConversationSummaryMemory(llm=llm)

# Hafıza ile chain
conversation_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)
```

---

## 🎯 İlk RAG Uygulaması

### Adım 1: Gerekli Kütüphaneleri Yükleyin
```bash
pip install langchain openai chromadb tiktoken
```

### Adım 2: Basit RAG Sistemi
```python
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import os

# API key'inizi ayarlayın
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# 1. Doküman yükleme
loader = TextLoader("belgeler/sirket_bilgileri.txt")
documents = loader.load()

# 2. Metni parçalara böl
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

# 3. Embedding'leri oluştur
embeddings = OpenAIEmbeddings()

# 4. Vektör veritabanı oluştur
db = Chroma.from_documents(docs, embeddings)

# 5. LLM'i başlat
llm = OpenAI(temperature=0)

# 6. RAG chain'i oluştur
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever()
)

# 7. Soru sor
query = "Şirketin çalışan sayısı kaç?"
result = qa_chain.run(query)
print(result)
```

### Adım 3: Gelişmiş RAG Sistemi
```python
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import PromptTemplate

# Özel prompt template
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    Aşağıdaki bilgileri kullanarak soruyu cevaplayın:
    
    Bilgiler: {context}
    
    Soru: {question}
    
    Cevap (Türkçe):
    """
)

# Kaynak belirtmeli RAG
qa_with_sources = RetrievalQAWithSourcesChain.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever(),
    return_source_documents=True
)

# Soru-cevap
query = "Şirketin ana faaliyet alanı nedir?"
result = qa_with_sources({"query": query})

print("Cevap:", result['result'])
print("Kaynaklar:", result['source_documents'])
```

---

## 🔍 Vektör Veritabanları ve Embedding

### Embedding Nedir?
Embedding, kelimeleri ve cümleleri **sayısal vektörlere** dönüştürme işlemidir.

#### Analoji: **Renklerin Koordinatları**
```
Kırmızı = [255, 0, 0]
Mavi = [0, 0, 255]
Mor = [128, 0, 128]  # Kırmızı + Mavi karışımı
```

#### Kelimeler için:
```
"Kedi" = [0.2, 0.8, 0.1, 0.9, ...]  # 1536 boyutlu vektör
"Köpek" = [0.3, 0.7, 0.2, 0.8, ...]  # Kediye benzer
"Araba" = [0.9, 0.1, 0.8, 0.2, ...]  # Kedi'den çok farklı
```

### Similarity Search (Benzerlik Araması)
```python
from langchain.embeddings import OpenAIEmbeddings
import numpy as np

embeddings = OpenAIEmbeddings()

# Kelime embedding'leri
texts = ["kedi", "köpek", "araba", "bisiklet"]
vectors = embeddings.embed_documents(texts)

# Benzerlik hesapla
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# "kedi" ile diğerlerinin benzerliği
query_vector = embeddings.embed_query("kedi")
for i, text in enumerate(texts):
    similarity = cosine_similarity(query_vector, vectors[i])
    print(f"{text}: {similarity:.3f}")
```

---

## 🎪 Gerçek Hayat Örneği: Müşteri Hizmetleri RAG

### Senaryo: E-ticaret sitesi müşteri hizmetleri
```python
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI

class MusteriHizmetleriRAG:
    def __init__(self):
        self.setup_rag()
    
    def setup_rag(self):
        # 1. Müşteri hizmetleri belgelerini yükle
        loader = DirectoryLoader(
            "musteri_belgeleri/",
            glob="*.txt",
            show_progress=True
        )
        documents = loader.load()
        
        # 2. Metni akıllı parçalara böl
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        docs = text_splitter.split_documents(documents)
        
        # 3. Vektör veritabanı oluştur
        embeddings = OpenAIEmbeddings()
        self.vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        
        # 4. Hafıza ekle
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # 5. Konuşmalı RAG chain'i oluştur
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=OpenAI(temperature=0.2),
            retriever=self.vectordb.as_retriever(search_kwargs={"k": 3}),
            memory=self.memory,
            return_source_documents=True
        )
    
    def musteri_sorusu(self, soru):
        """Müşteri sorusunu yanıtla"""
        result = self.qa_chain({"question": soru})
        return {
            "cevap": result["answer"],
            "kaynaklar": result["source_documents"]
        }

# Kullanım
musteri_bot = MusteriHizmetleriRAG()

# Örnek sorular
sorular = [
    "İade politikanız nedir?",
    "Kargo ne kadar sürer?",
    "Ürün garantisi var mı?",
    "İptal edebilir miyim?"
]

for soru in sorular:
    print(f"\n🙋‍♂️ Müşteri: {soru}")
    cevap = musteri_bot.musteri_sorusu(soru)
    print(f"🤖 Bot: {cevap['cevap']}")
```

---

## 🚨 Önemli Notlar ve İpuçları

### 1. **API Key Yönetimi**
```python
# ❌ Yanlış - kod içinde API key
llm = OpenAI(openai_api_key="sk-xxxxxxxx")

# ✅ Doğru - environment variable
import os
os.environ["OPENAI_API_KEY"] = "your-key"
llm = OpenAI()

# ✅ Daha güvenli - .env dosyası
from dotenv import load_dotenv
load_dotenv()
llm = OpenAI()
```

### 2. **Chunk Size Optimizasyonu**
```python
# Farklı chunk boyutları deneyin
splitters = [
    CharacterTextSplitter(chunk_size=500, chunk_overlap=50),   # Küçük
    CharacterTextSplitter(chunk_size=1000, chunk_overlap=100), # Orta
    CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)  # Büyük
]

# Hangisi daha iyi sonuç veriyor test edin
```

### 3. **Maliyet Kontrolü**
```python
from langchain.callbacks import get_openai_callback

# Token kullanımını takip edin
with get_openai_callback() as cb:
    result = qa_chain.run("Soru")
    print(f"Toplam token: {cb.total_tokens}")
    print(f"Maliyet: ${cb.total_cost}")
```

---

## 🎯 Bölüm 1 Özeti

Bu bölümde öğrendikleriniz:

### ✅ **Temel Kavramlar:**
- LangChain'in ne olduğu ve neden önemli olduğu
- RAG konsepti ve nasıl çalıştığı
- Embedding ve vektör veritabanları

### ✅ **Pratik Beceriler:**
- İlk RAG uygulamanızı oluşturma
- Doküman yükleme ve parçalara ayırma
- Vektör veritabanı kullanma

### ✅ **Gerçek Proje:**
- Müşteri hizmetleri RAG sistemi

### 🔜 **Sonraki Bölümde:**
- LangChain'in gelişmiş özellikleri
- Farklı Chain türleri
- Agent'lar ve Tools
- Memory sistemleri

---

**Not:** Bu doküman serisi devam edecek. Her bölüm bir öncekini temel alacak şekilde tasarlanmıştır.