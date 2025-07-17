# LangChain ve RAG Ekosistemi - Bölüm 3: ChromaDB ve Vektör Veritabanları

## 🎯 ChromaDB Nedir?

### Basit Anlatım
ChromaDB'yi **akıllı kütüphane katalog sistemi** olarak düşünün. Geleneksel kütüphanede kitaplar alfabetik sıraya göre dizilirken, ChromaDB kitapları **konularına göre** organize eder.

### Analoji: **İnsan Beynindeki Anılar**
```
Geleneksel DB:     "Anıları tarihe göre sırala"
                   2020 → 2021 → 2022 → 2023

ChromaDB:          "Benzer anıları yakın tut"
                   Mutlu anılar ← → Üzücü anılar
                        ↑              ↓
                   Aile anıları ← → İş anıları
```

### ChromaDB'nin Avantajları
- **🚀 Hızlı benzerlik araması**: Milyonlarca doküman içinde saniyeler içinde
- **🔧 Kolay kurulum**: Docker ile 1 komutta çalışır
- **📈 Otomatik ölçekleme**: Verileriniz büyüdükçe kendini optimize eder
- **🔗 LangChain entegrasyonu**: Seamless integration
- **💾 Persistent storage**: Verileriniz güvenle saklanır

---

## 🛠️ ChromaDB Kurulum ve İlk Adımlar

### Kurulum Yöntemleri

#### 1. **Temel Sorgulama**
```python
# Basit benzerlik araması
basic_results = collection.query(
    query_texts=["Python programlama"],
    n_results=5
)

print("Temel arama sonuçları:")
for doc in basic_results['documents'][0]:
    print(f"- {doc}")
```

### 2. **Metadata Filtreleme**
```python
# Metadata ile filtreleme
filtered_results = collection.query(
    query_texts=["Python öğrenme"],
    n_results=10,
    where={"category": "tech"}  # Sadece teknoloji kategorisi
)

# Karmaşık filtreler
complex_filter = collection.query(
    query_texts=["veri analizi"],
    n_results=5,
    where={
        "$and": [
            {"category": "tech"},
            {"word_count": {"$gt": 10}},  # 10'dan fazla kelime
            {"$or": [
                {"priority": "high"},
                {"updated": True}
            ]}
        ]
    }
)

# Tarih bazlı filtreleme
date_filter = collection.query(
    query_texts=["machine learning"],
    where={"created_date": {"$gte": "2024-01-01"}},
    n_results=3
)
```

### 3. **Embedding ile Direkt Arama**
```python
import numpy as np

# Kendi embedding'inizi kullanın
custom_embedding = np.random.rand(384).tolist()  # SentenceTransformer boyutu

embedding_results = collection.query(
    query_embeddings=[custom_embedding],
    n_results=5,
    include=["documents", "distances", "metadatas"]
)

print("Embedding ile arama:")
for i, doc in enumerate(embedding_results['documents'][0]):
    distance = embedding_results['distances'][0][i]
    metadata = embedding_results['metadatas'][0][i]
    print(f"Mesafe: {distance:.3f} - {doc[:50]}...")
```

### 4. **Include/Exclude Parametreleri**
```python
# Sadece belirli alanları getir
minimal_results = collection.query(
    query_texts=["artificial intelligence"],
    n_results=3,
    include=["documents", "distances"]  # metadatas dahil değil
)

# Her şeyi getir
full_results = collection.query(
    query_texts=["deep learning"],
    n_results=3,
    include=["documents", "metadatas", "distances", "embeddings"]
)

print("Embedding boyutu:", len(full_results['embeddings'][0][0]))
```

---

## 🚀 ChromaDB ile LangChain Entegrasyonu

### Temel Entegrasyon
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings, SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Embedding modeli seç
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Dokümanları yükle
loader = DirectoryLoader("./documents", glob="*.txt")
documents = loader.load()

# Metni böl
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
splits = text_splitter.split_documents(documents)

# ChromaDB ile vectorstore oluştur
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_langchain"
)

# RAG chain oluştur
llm = OpenAI(temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)

# Soru-cevap
response = qa_chain.run("ChromaDB nasıl çalışır?")
print(response)
```

### Gelişmiş ChromaDB + LangChain Projesi
```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.llms import OpenAI
import os

class GelismisRAGSistemi:
    def __init__(self, persist_directory="./advanced_chroma"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0.2)
        self.vectorstore = None
        self.qa_chain = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
    def belgeler_yukle(self, file_paths, web_urls=None):
        """Çeşitli kaynaklardan belge yükle"""
        documents = []
        
        # Dosyalardan yükle
        for file_path in file_paths:
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())
        
        # Web sitelerinden yükle
        if web_urls:
            for url in web_urls:
                loader = WebBaseLoader(url)
                documents.extend(loader.load())
        
        return documents
    
    def metni_parcala(self, documents):
        """Dokümanlari optimal parçalara böl"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_documents(documents)
    
    def veritabani_olustur(self, splits):
        """ChromaDB veritabanını oluştur"""
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )
        
        # Veritabanını kalıcı hale getir
        self.vectorstore.persist()
        
    def mevcut_veritabani_yukle(self):
        """Mevcut ChromaDB'yi yükle"""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return True
        return False
    
    def qa_chain_olustur(self):
        """Konuşmalı QA chain'i oluştur"""
        retriever = self.vectorstore.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance
            search_kwargs={
                "k": 5,
                "fetch_k": 10,
                "lambda_mult": 0.7
            }
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,
            verbose=True
        )
    
    def soru_sor(self, question):
        """Soru sor ve kaynaklarla birlikte cevap al"""
        if not self.qa_chain:
            raise ValueError("QA chain oluşturulmadı!")
        
        result = self.qa_chain({"question": question})
        
        return {
            "answer": result["answer"],
            "sources": result["source_documents"],
            "chat_history": result["chat_history"]
        }
    
    def benzer_belgeleri_bul(self, query, k=5):
        """Benzer belgeleri bul"""
        docs = self.vectorstore.similarity_search_with_score(query, k=k)
        return docs
    
    def istatistikleri_goster(self):
        """Veritabanı istatistikleri"""
        if self.vectorstore:
            # ChromaDB collection bilgileri
            collection = self.vectorstore._collection
            count = collection.count()
            
            print(f"Toplam doküman: {count}")
            print(f"Collection adı: {collection.name}")
            print(f"Embedding modeli: {type(self.embeddings).__name__}")

# Kullanım örneği
def main():
    # Sistem oluştur
    rag_sistem = GelismisRAGSistemi()
    
    # Mevcut veritabanını yükle veya yeni oluştur
    if not rag_sistem.mevcut_veritabani_yukle():
        print("Yeni veritabanı oluşturuluyor...")
        
        # Belgeleri yükle
        documents = rag_sistem.belgeler_yukle(
            file_paths=["./docs/manual.txt", "./docs/faq.pdf"],
            web_urls=["https://docs.python.org/3/tutorial/"]
        )
        
        # Metni parçala
        splits = rag_sistem.metni_parcala(documents)
        print(f"{len(splits)} parça oluşturuldu")
        
        # Veritabanını oluştur
        rag_sistem.veritabani_olustur(splits)
        print("Veritabanı oluşturuldu ve kaydedildi")
    else:
        print("Mevcut veritabanı yüklendi")
    
    # QA chain oluştur
    rag_sistem.qa_chain_olustur()
    
    # İstatistikleri göster
    rag_sistem.istatistikleri_goster()
    
    # Örnek sorular
    sorular = [
        "Python'da döngüler nasıl çalışır?",
        "Hangi veri yapıları kullanabilirim?",
        "Error handling nasıl yapılır?",
        "Bu konulardan hangisini önce öğrenmeliyim?"
    ]
    
    print("\n" + "="*50)
    print("SORU-CEVAP SESSİYONU")
    print("="*50)
    
    for soru in sorular:
        print(f"\n🙋‍♂️ Soru: {soru}")
        
        try:
            result = rag_sistem.soru_sor(soru)
            print(f"🤖 Cevap: {result['answer']}")
            
            print("\n📚 Kaynaklar:")
            for i, source in enumerate(result['sources'][:2], 1):
                print(f"{i}. {source.page_content[:100]}...")
                
        except Exception as e:
            print(f"❌ Hata: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()
```

---

## 🔧 ChromaDB Optimizasyon Teknikleri

### 1. **Index Optimizasyonu**
```python
# HNSW parametrelerini ayarla
collection = client.create_collection(
    name="optimized_collection",
    metadata={
        "hnsw:space": "cosine",           # cosine, l2, ip
        "hnsw:construction_ef": 200,      # İnşa kalitesi (varsayılan: 200)
        "hnsw:M": 16,                     # Bağlantı sayısı (varsayılan: 16)
        "hnsw:search_ef": 100,            # Arama kalitesi (varsayılan: 10)
        "hnsw:num_threads": 4             # Thread sayısı
    }
)
```

### 2. **Batch Ekleme Optimizasyonu**
```python
def optimize_batch_insert(collection, documents, batch_size=1000):
    """Büyük veri setleri için optimize edilmiş ekleme"""
    total_docs = len(documents)
    
    for i in range(0, total_docs, batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_ids = [f"doc_{j}" for j in range(i, min(i+batch_size, total_docs))]
        
        collection.add(
            documents=batch_docs,
            ids=batch_ids
        )
        
        print(f"İşlenen: {min(i+batch_size, total_docs)}/{total_docs}")
    
    print("Tüm dokümanlar eklendi!")

# Kullanım
large_documents = ["Doküman " + str(i) for i in range(10000)]
optimize_batch_insert(collection, large_documents)
```

### 3. **Memory ve Disk Optimizasyonu**
```python
# Persistent client ile disk kullanımı
persistent_client = chromadb.PersistentClient(
    path="./optimized_storage",
    settings=Settings(
        chroma_server_host="localhost",
        chroma_server_http_port=8000,
        chroma_server_grpc_port=8001,
        anonymized_telemetry=False
    )
)

# Memory mapping ayarları
collection = persistent_client.create_collection(
    name="memory_optimized",
    metadata={
        "hnsw:batch_size": 1000,
        "hnsw:sync_threshold": 1000
    }
)
```

### 4. **Arama Performansı Optimizasyonu**
```python
class OptimizedRetriever:
    def __init__(self, collection):
        self.collection = collection
        self.cache = {}  # Basit cache
    
    def search_with_cache(self, query, n_results=5, cache_enabled=True):
        """Cache ile optimized arama"""
        cache_key = f"{query}_{n_results}"
        
        if cache_enabled and cache_key in self.cache:
            print("Cache'den sonuç döndürülüyor")
            return self.cache[cache_key]
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if cache_enabled:
            self.cache[cache_key] = results
        
        return results
    
    def bulk_search(self, queries, n_results=5):
        """Toplu arama optimizasyonu"""
        return self.collection.query(
            query_texts=queries,  # Birden fazla sorgu aynı anda
            n_results=n_results
        )

# Kullanım
retriever = OptimizedRetriever(collection)

# Tekli arama
result1 = retriever.search_with_cache("Python programlama")
result2 = retriever.search_with_cache("Python programlama")  # Cache'den

# Toplu arama
bulk_results = retriever.bulk_search([
    "machine learning",
    "deep learning", 
    "neural networks"
])
```

---

## 📊 ChromaDB Monitoring ve Analytics

### 1. **Performans İzleme**
```python
import time
from collections import defaultdict

class ChromaDBMonitor:
    def __init__(self, collection):
        self.collection = collection
        self.metrics = defaultdict(list)
    
    def timed_query(self, query, n_results=5):
        """Sorgu süresini ölç"""
        start_time = time.time()
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        end_time = time.time()
        query_time = end_time - start_time
        
        self.metrics['query_times'].append(query_time)
        self.metrics['query_count'].append(1)
        
        print(f"Sorgu süresi: {query_time:.3f}s")
        return results
    
    def get_performance_stats(self):
        """Performans istatistikleri"""
        if self.metrics['query_times']:
            avg_time = sum(self.metrics['query_times']) / len(self.metrics['query_times'])
            max_time = max(self.metrics['query_times'])
            min_time = min(self.metrics['query_times'])
            total_queries = sum(self.metrics['query_count'])
            
            return {
                'average_query_time': avg_time,
                'max_query_time': max_time,
                'min_query_time': min_time,
                'total_queries': total_queries
            }
        return {}

# Kullanım
monitor = ChromaDBMonitor(collection)

# Test sorguları
test_queries = [
    "Python nedir",
    "Machine learning algorithms",
    "Data visualization techniques",
    "Web development frameworks"
]

for query in test_queries:
    monitor.timed_query(query)

stats = monitor.get_performance_stats()
print("Performans İstatistikleri:", stats)
```

### 2. **Veri Analizi**
```python
def analyze_collection(collection):
    """Collection'ın detaylı analizi"""
    
    # Toplam doküman sayısı
    total_docs = collection.count()
    
    # Örnek dokümanları al
    sample_results = collection.query(
        query_texts=["sample"],
        n_results=min(100, total_docs),
        include=["documents", "metadatas", "embeddings"]
    )
    
    if sample_results['documents']:
        documents = sample_results['documents'][0]
        metadatas = sample_results['metadatas'][0]
        embeddings = sample_results['embeddings'][0]
        
        # Doküman uzunluk analizi
        doc_lengths = [len(doc.split()) for doc in documents]
        avg_length = sum(doc_lengths) / len(doc_lengths)
        
        # Metadata analizi
        categories = defaultdict(int)
        for meta in metadatas:
            if 'category' in meta:
                categories[meta['category']] += 1
        
        # Embedding analizi
        embedding_dim = len(embeddings[0]) if embeddings else 0
        
        analysis = {
            'total_documents': total_docs,
            'average_document_length': avg_length,
            'embedding_dimension': embedding_dim,
            'category_distribution': dict(categories),
            'sample_size': len(documents)
        }
        
        print("📊 Collection Analizi:")
        print(f"Toplam doküman: {analysis['total_documents']}")
        print(f"Ortalama kelime sayısı: {analysis['average_document_length']:.1f}")
        print(f"Embedding boyutu: {analysis['embedding_dimension']}")
        print(f"Kategori dağılımı: {analysis['category_distribution']}")
        
        return analysis
    
    return {"total_documents": total_docs, "error": "Doküman bulunamadı"}

# Analiz çalıştır
analysis_result = analyze_collection(collection)
```

---

## 🎯 Gerçek Hayat Projesi: Akıllı Doküman Arama Sistemi

```python
import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.llms import OpenAI
import os
import json
from datetime import datetime

class AkilliDokumanSistemi:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./akilli_sistem")
        self.embeddings = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0.1)
        self.collections = {}
        
    def koleksiyon_olustur(self, name, description=""):
        """Yeni koleksiyon oluştur"""
        try:
            collection = self.client.create_collection(
                name=name,
                metadata={
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                    "total_docs": 0
                }
            )
            self.collections[name] = collection
            print(f"✅ '{name}' koleksiyonu oluşturuldu")
            return collection
        except Exception as e:
            print(f"❌ Koleksiyon oluşturma hatası: {e}")
            return None
    
    def mevcut_koleksiyonlari_yukle(self):
        """Mevcut koleksiyonları yükle"""
        collections = self.client.list_collections()
        for col in collections:
            self.collections[col.name] = col
        print(f"📚 {len(self.collections)} koleksiyon yüklendi")
    
    def belge_yukle_ve_islet(self, collection_name, file_path, chunk_size=1000):
        """Belgeyi yükle ve işle"""
        if collection_name not in self.collections:
            print(f"❌ '{collection_name}' koleksiyonu bulunamadı")
            return False
        
        try:
            # Dosya türüne göre loader seç
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(('.txt', '.md')):
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                print(f"❌ Desteklenmeyen dosya türü: {file_path}")
                return False
            
            # Dokümanı yükle
            documents = loader.load()
            
            # Metni parçala
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=200,
                length_function=len
            )
            splits = text_splitter.split_documents(documents)
            
            # ChromaDB'ye ekle
            collection = self.collections[collection_name]
            
            # Her chunk için unique ID ve metadata oluştur
            ids = []
            texts = []
            metadatas = []
            
            for i, split in enumerate(splits):
                doc_id = f"{os.path.basename(file_path)}_{i:04d}"
                ids.append(doc_id)
                texts.append(split.page_content)
                
                metadata = {
                    "source_file": file_path,
                    "chunk_index": i,
                    "total_chunks": len(splits),
                    "word_count": len(split.page_content.split()),
                    "processed_at": datetime.now().isoformat()
                }
                
                # Sayfa numarası varsa ekle
                if hasattr(split, 'metadata') and 'page' in split.metadata:
                    metadata['page'] = split.metadata['page']
                
                metadatas.append(metadata)
            
            # Batch ekleme
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ {file_path} dosyası işlendi ({len(splits)} parça)")
            return True
            
        except Exception as e:
            print(f"❌ Belge işleme hatası: {e}")
            return False
    
    def dizin_islet(self, collection_name, directory_path, file_patterns=["*.txt", "*.pdf", "*.md"]):
        """Tüm dizini işle"""
        success_count = 0
        total_count = 0
        
        for pattern in file_patterns:
            loader = DirectoryLoader(directory_path, glob=pattern)
            try:
                documents = loader.load()
                total_count += len(documents)
                
                for doc in documents:
                    if self.belge_yukle_ve_islet(collection_name, doc.metadata['source']):
                        success_count += 1
            except Exception as e:
                print(f"❌ Dizin işleme hatası ({pattern}): {e}")
        
        print(f"📊 Sonuç: {success_count}/{total_count} dosya başarıyla işlendi")
    
    def akilli_arama(self, collection_name, query, n_results=5, filter_criteria=None):
        """Gelişmiş arama"""
        if collection_name not in self.collections:
            return {"error": "Koleksiyon bulunamadı"}
        
        collection = self.collections[collection_name]
        
        try:
            # Arama parametreleri
            search_params = {
                "query_texts": [query],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]
            }
            
            # Filter ekle
            if filter_criteria:
                search_params["where"] = filter_criteria
            
            results = collection.query(**search_params)
            
            # Sonuçları formatla
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i],  # Distance to similarity
                    "rank": i + 1
                })
            
            return {
                "query": query,
                "total_results": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            return {"error": f"Arama hatası: {e}"}
    
    def soru_cevap(self, collection_name, question):
        """RAG ile soru-cevap"""
        try:
            # LangChain vectorstore oluştur
            vectorstore = Chroma(
                client=self.client,
                collection_name=collection_name,
                embedding_function=self.embeddings
            )
            
            # QA chain oluştur
            qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            # Soruyu cevapla
            result = qa_chain({"question": question})
            
            return {
                "question": question,
                "answer": result["answer"],
                "sources": [doc.page_content for doc in result["source_documents"]],
                "source_metadata": [doc.metadata for doc in result["source_documents"]]
            }
            
        except Exception as e:
            return {"error": f"Soru-cevap hatası: {e}"}
    
    def koleksiyon_istatistikleri(self, collection_name):
        """Koleksiyon istatistikleri"""
        if collection_name not in self.collections:
            return {"error": "Koleksiyon bulunamadı"}
        
        collection = self.collections[collection_name]
        
        try:
            # Temel istatistikler
            total_docs = collection.count()
            
            # Örnek veriler al
            sample = collection.query(
                query_texts=["sample"],
                n_results=min(100, total_docs),
                include=["metadatas", "documents"]
            )
            
            if sample['metadatas']:
                # Dosya dağılımı
                source_files = {}
                word_counts = []
                
                for meta, doc in zip(sample['metadatas'][0], sample['documents'][0]):
                    source_file = meta.get('source_file', 'unknown')
                    source_files[source_file] = source_files.get(source_file, 0) + 1
                    word_counts.append(len(doc.split()))
                
                avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
                
                return {
                    "total_documents": total_docs,
                    "source_files": source_files,
                    "average_words_per_chunk": avg_words,
                    "total_source_files": len(source_files)
                }
            
            return {"total_documents": total_docs}
            
        except Exception as e:
            return {"error": f"İstatistik hatası: {e}"}

# Demo kullanımı
def demo_sistem():
    print("🚀 Akıllı Doküman Arama Sistemi Demo")
    print("=" * 50)
    
    # Sistem oluştur
    sistem = AkilliDokumanSistemi()
    
    # Mevcut koleksiyonları yükle
    sistem.mevcut_koleksiyonlari_yukle()
    
    # Yeni koleksiyon oluştur
    sistem.koleksiyon_olustur("python_docs", "Python dokümantasyonu ve örnekleri")
    
    # Örnek dosyalar (gerçek dosya yollarını kullanın)
    # sistem.belge_yukle_ve_islet("python_docs", "./docs/python_tutorial.pdf")
    # sistem.belge_yukle_ve_islet("python_docs", "./docs/python_reference.txt")
    
    # Akıllı arama testi
    print("\n🔍 Arama Testi:")
    arama_sonucu = sistem.akilli_arama(
        "python_docs", 
        "Python döngüleri nasıl çalışır",
        n_results=3
    )
    
    if "error" not in arama_sonucu:
        for result in arama_sonucu["results"]:
            print(f"📄 Skor: {result['similarity_score']:.3f}")
            print(f"📝 İçerik: {result['content'][:100]}...")
            print(f"📊 Metadata: {result['metadata']['source_file']}")
            print("-" * 30)
    
    # Soru-cevap testi
    print("\n💬 Soru-Cevap Testi:")
    qa_sonucu = sistem.soru_cevap(
        "python_docs",
        "Python'da for döngüsü nasıl kullanılır?"
    )
    
    if "error" not in qa_sonucu:
        print(f"❓ Soru: {qa_sonucu['question']}")
        print(f"✅ Cevap: {qa_sonucu['answer']}")
        print(f"📚 Kaynak sayısı: {len(qa_sonucu['sources'])}")
    
    # İstatistikler
    print("\n📊 Koleksiyon İstatistikleri:")
    stats = sistem.koleksiyon_istatistikleri("python_docs")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    demo_sistem()
```

---

## 🔍 ChromaDB vs Diğer Vektör Veritabanları

### Karşılaştırma Tablosu

| Özellik | ChromaDB | Pinecone | Weaviate | FAISS |
|---------|----------|----------|----------|-------|
| **Kurulum** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Performans** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ölçeklenebilirlik** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Maliyet** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **LangChain Entegrasyonu** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

### Hangi Durumlarda ChromaDB?

#### ✅ **ChromaDB İdeal:**
- Prototip geliştirme
- Küçük-orta ölçekli projeler
- Local development
- Açık kaynak projeler
- LangChain ile hızlı entegrasyon

#### ⚠️ **ChromaDB Sınırlı:**
- Çok büyük ölçekli projeler (milyonlarca doküman)
- High-throughput production sistemleri
- Complex distributed architectures

---

## 🛠️ ChromaDB Best Practices

### 1. **Veri Modelleme**
```python
# ✅ İyi metadata tasarımı
good_metadata = {
    "document_type": "article",           # Categorical
    "created_date": "2024-01-15",        # Date
    "word_count": 1500,                  # Numeric
    "tags": ["python", "tutorial"],     # Array
    "priority": "high",                  # Enum
    "author": "john_doe",                # String ID
    "version": "1.2"                     # Version
}

# ❌ Kötü metadata tasarımı
bad_metadata = {
    "info": "Bu bir makale 2024-01-15 tarihinde john_doe tarafından yazıldı",  # Mixed data
    "misc": {"a": 1, "b": {"c": 2}},     # Nested objects
    "very_long_text": "Bu çok uzun bir metin..."  # Large text in metadata
}
```

### 2. **Chunk Stratejileri**
```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    SpacyTextSplitter
)

# Doküman türüne göre splitter seçimi
def choose_splitter(document_type, content_length):
    if document_type == "code":
        # Kod için özel ayırıcılar
        return RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\nclass ", "\ndef ", "\n", " "]
        )
    elif document_type == "academic":
        # Akademik makaleler için
        return RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " "]
        )
    elif content_length > 10000:
        # Uzun dokümanlar için
        return TokenTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    else:
        # Genel amaçlı
        return RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

# Kullanım
splitter = choose_splitter("academic", 15000)
chunks = splitter.split_text(document_content)
```

### 3. **Güvenlik ve Erişim Kontrolü**
```python
import hashlib
import jwt
from datetime import datetime, timedelta

class SecureChromaDB:
    def __init__(self, secret_key):
        self.client = chromadb.Client()
        self.secret_key = secret_key
        self.user_collections = {}
    
    def create_user_token(self, user_id, permissions):
        """Kullanıcı token'ı oluştur"""
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token):
        """Token doğrula"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def hash_sensitive_data(self, data):
        """Hassas veriyi hashle"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def create_collection_with_access(self, token, collection_name, is_private=True):
        """Erişim kontrolü ile koleksiyon oluştur"""
        user_data = self.verify_token(token)
        if not user_data:
            raise ValueError("Geçersiz token")
        
        if is_private:
            # Private collection adını hash'le
            hashed_name = f"{user_data['user_id']}_{self.hash_sensitive_data(collection_name)[:10]}"
        else:
            hashed_name = collection_name
        
        collection = self.client.create_collection(
            name=hashed_name,
            metadata={
                "owner": user_data['user_id'],
                "private": is_private,
                "created_at": datetime.now().isoformat()
            }
        )
        
        self.user_collections[user_data['user_id']] = self.user_collections.get(user_data['user_id'], [])
        self.user_collections[user_data['user_id']].append(hashed_name)
        
        return collection
```

### 4. **Performance Monitoring**
```python
import psutil
import time
from functools import wraps

def monitor_performance(func):
    """Performance monitoring decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Başlangıç metrikleri
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            
            # Son metrikleri
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            # Log performance
            duration = end_time - start_time
            memory_diff = end_memory - start_memory
            
            print(f"⏱️ {func.__name__} - Süre: {duration:.3f}s, Bellek: {memory_diff:+.1f}MB")
            
            return result
            
        except Exception as e:
            print(f"❌ {func.__name__} - Hata: {e}")
            raise
    
    return wrapper

# Kullanım
class MonitoredChromaDB:
    def __init__(self):
        self.client = chromadb.Client()
    
    @monitor_performance
    def add_documents(self, collection, documents, metadatas, ids):
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    @monitor_performance
    def query_documents(self, collection, query, n_results=5):
        return collection.query(
            query_texts=[query],
            n_results=n_results
        )
```

---

## 🎯 Bölüm 3 Özeti

Bu bölümde öğrendikleriniz:

### ✅ **ChromaDB Temelleri:**
- ChromaDB'nin ne olduğu ve avantajları
- Kurulum ve temel kullanım
- Embedding sistemlerinin detaylı açıklaması

### ✅ **Veri Yönetimi:**
- Collection oluşturma ve yönetimi
- Batch işlemler ve optimizasyon
- Metadata tasarımı ve filtreleme

### ✅ **Gelişmiş Özellikler:**
- LangChain entegrasyonu
- Performance monitoring
- Security ve access control

### ✅ **Gerçek Proje:**
- Akıllı doküman arama sistemi
- Multi-source data loading
- Advanced search ve QA capabilities

### 🔜 **Sonraki Bölümde:**
- LangGraph detayları
- Complex workflow design
- Multi-agent systems
- State management

ChromaDB ile vektör veritabanlarının temellerini ve ileri seviye kullanımını öğrendiniz. Sonraki bölümde LangGraph ile karmaşık iş akışları tasarlamayı göreceğiz.. **Pip ile Kurulum**
```bash
# Temel kurulum
pip install chromadb

# Tüm özelliklerle
pip install "chromadb[all]"

# LangChain ile birlikte
pip install chromadb langchain openai tiktoken
```

#### 2. **Docker ile Kurulum**
```bash
# ChromaDB server'ı çalıştır
docker run -p 8000:8000 chromadb/chroma

# Docker Compose ile
version: '3.8'
services:
  chromadb:
    image: chromadb/chroma
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_PORT=8000
```

### İlk ChromaDB Uygulaması
```python
import chromadb
from chromadb.config import Settings

# Client oluştur
client = chromadb.Client()

# Koleksiyon oluştur
collection = client.create_collection(
    name="ilk_koleksiyonum",
    metadata={"description": "İlk ChromaDB denemem"}
)

# Doküman ekle
collection.add(
    documents=[
        "Python bir programlama dilidir",
        "JavaScript web geliştirmede kullanılır",
        "SQL veritabanı sorgulama dilidir",
        "HTML web sayfalarının iskeletini oluşturur"
    ],
    metadatas=[
        {"category": "programming", "difficulty": "beginner"},
        {"category": "web", "difficulty": "beginner"},
        {"category": "database", "difficulty": "intermediate"},
        {"category": "web", "difficulty": "easy"}
    ],
    ids=["doc1", "doc2", "doc3", "doc4"]
)

# Benzerlik araması
results = collection.query(
    query_texts=["web geliştirme nasıl yapılır"],
    n_results=2
)

print("Bulunan dokümanlar:")
for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc}")
    print(f"   Mesafe: {results['distances'][0][i]}")
    print(f"   Metadata: {results['metadatas'][0][i]}")
```

---

## 🧠 Embedding'ler Derinlemesine

### Embedding Nedir? (Detaylı Açıklama)

#### Analoji: **GPS Koordinatları**
```python
# Şehirler için koordinatlar
istanbul = [41.0082, 28.9784]   # Enlem, Boylam
ankara = [39.9334, 32.8597]
izmir = [38.4237, 27.1428]

# İstanbul'a en yakın şehir hangisi?
def mesafe_hesapla(koord1, koord2):
    # Euclidean distance
    return ((koord1[0] - koord2[0])**2 + (koord1[1] - koord2[1])**2)**0.5

istanbul_ankara = mesafe_hesapla(istanbul, ankara)
istanbul_izmir = mesafe_hesapla(istanbul, izmir)

print(f"İstanbul-Ankara: {istanbul_ankara}")
print(f"İstanbul-İzmir: {istanbul_izmir}")
```

#### Kelimeler için Benzer Sistem
```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Çok boyutlu kelime embeddingleri
model = SentenceTransformer('all-MiniLM-L6-v2')

sentences = [
    "Kedi sevimli bir hayvandır",
    "Köpek sadık bir dosttur", 
    "Araba ulaşım aracıdır",
    "Otobüs toplu taşıma aracıdır"
]

# Embeddingleri hesapla
embeddings = model.encode(sentences)

print(f"Her cümle {embeddings.shape[1]} boyutlu vektöre dönüştü")
print(f"İlk cümlenin ilk 5 değeri: {embeddings[0][:5]}")

# Benzerlik hesapla
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# "Kedi" cümlesi ile diğerlerinin benzerliği
base_embedding = embeddings[0]  # Kedi cümlesi
for i, sentence in enumerate(sentences[1:], 1):
    similarity = cosine_similarity(base_embedding, embeddings[i])
    print(f"'{sentences[0]}' vs '{sentence}': {similarity:.3f}")
```

### ChromaDB ile Custom Embeddings
```python
from chromadb.utils import embedding_functions

# Farklı embedding modelleri
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-openai-key",
    model_name="text-embedding-ada-002"
)

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Özel embedding fonksiyonu
class CustomEmbeddingFunction:
    def __call__(self, input):
        # Kendi embedding algoritmanız
        # Örnek: TF-IDF, Word2Vec, FastText
        embeddings = self.custom_embedding_logic(input)
        return embeddings
    
    def custom_embedding_logic(self, texts):
        # Basit örnek: karakter frekansı tabanlı
        embeddings = []
        for text in texts:
            # Her harf için frekans sayısı (26 boyutlu vektör)
            vector = [0] * 26
            for char in text.lower():
                if 'a' <= char <= 'z':
                    vector[ord(char) - ord('a')] += 1
            embeddings.append(vector)
        return embeddings

# Kullanım
collection = client.create_collection(
    name="custom_embeddings",
    embedding_function=sentence_transformer_ef
)
```

---

## 📊 ChromaDB ile Veri Yönetimi

### Collection İşlemleri

#### 1. **Collection Oluşturma ve Yönetimi**
```python
import chromadb
from datetime import datetime

client = chromadb.PersistentClient(path="./chroma_storage")

# Gelişmiş collection oluşturma
collection = client.create_collection(
    name="sirket_belgeleri",
    metadata={
        "description": "Şirket dokümanları ve politikaları",
        "created_at": datetime.now().isoformat(),
        "version": "1.0",
        "total_documents": 0
    }
)

# Collection listesi
collections = client.list_collections()
print("Mevcut koleksiyonlar:")
for col in collections:
    print(f"- {col.name}: {col.metadata}")

# Collection bilgileri
info = collection.count()
print(f"Toplam doküman sayısı: {info}")
```

#### 2. **Batch İşlemler**
```python
# Büyük veri setleri için batch işlem
documents = []
metadatas = []
ids = []

# 1000 doküman ekleyelim
for i in range(1000):
    documents.append(f"Bu {i+1}. doküman. Python, veri bilimi ve AI hakkında bilgi içerir.")
    metadatas.append({
        "doc_id": i+1,
        "category": "tech" if i % 2 == 0 else "general",
        "word_count": len(f"Bu {i+1}. doküman...".split()),
        "created_date": "2024-01-01"
    })
    ids.append(f"doc_{i+1:04d}")

# Batch ekleme (chromadb otomatik olarak batch'lere böler)
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"Toplam {len(documents)} doküman eklendi")
```

#### 3. **Güncelleme ve Silme**
```python
# Doküman güncelleme
collection.update(
    ids=["doc_0001"],
    documents=["Güncellenmiş Python dokümanı - daha detaylı bilgiler"],
    metadatas=[{"category": "tech", "updated": True}]
)

# Upsert (yoksa ekle, varsa güncelle)
collection.upsert(
    ids=["doc_9999"],
    documents=["Yeni eklenen özel doküman"],
    metadatas=[{"category": "special", "priority": "high"}]
)

# Doküman silme
collection.delete(ids=["doc_0500", "doc_0501"])

# Koşullu silme
collection.delete(where={"category": "temp"})
```

---

## 🔍 Gelişmiş Sorgulama Teknikleri

### 1