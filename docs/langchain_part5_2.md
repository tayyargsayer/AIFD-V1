            elif any(word in query for word in ["compare", "difference", "versus"]):
                intent = "comparison"
            elif any(word in query for word in ["summarize", "summary", "overview"]):
                intent = "summarization"
            else:
                intent = "general_query"
            
            return {
                **state,
                "intent": intent,
                "metadata": {**state.get("metadata", {}), "intent_classified": True}
            }
        
        def knowledge_retrieval_node(state: SystemState) -> SystemState:
            """Knowledge retrieval using agent"""
            query = state["query"]
            
            try:
                if self.vectorstore:
                    knowledge_response = self.knowledge_agent.run(
                        f"Retrieve and summarize relevant information about: {query}"
                    )
                    
                    # Get source documents for transparency
                    source_docs = self.vectorstore.similarity_search(query, k=2)
                    sources = [doc.metadata.get("source", "unknown") for doc in source_docs]
                    
                    agent_responses = state.get("agent_responses", {})
                    agent_responses["knowledge"] = knowledge_response
                    
                    return {
                        **state,
                        "agent_responses": agent_responses,
                        "knowledge_sources": sources,
                        "context": {
                            **state.get("context", {}),
                            "knowledge_retrieved": True,
                            "source_count": len(sources)
                        }
                    }
                else:
                    return {
                        **state,
                        "agent_responses": {**state.get("agent_responses", {}), "knowledge": "No knowledge base available"},
                        "knowledge_sources": []
                    }
            except Exception as e:
                logger.error(f"Knowledge retrieval error: {e}")
                return {
                    **state,
                    "agent_responses": {**state.get("agent_responses", {}), "knowledge": f"Error: {str(e)}"},
                    "knowledge_sources": []
                }
        
        def analysis_node(state: SystemState) -> SystemState:
            """Analysis using specialized agent"""
            query = state["query"]
            knowledge_response = state.get("agent_responses", {}).get("knowledge", "")
            
            try:
                analysis_prompt = f"""
                Query: {query}
                Knowledge Context: {knowledge_response}
                
                Please provide detailed analysis.
                """
                
                analysis_response = self.analysis_agent.run(analysis_prompt)
                
                agent_responses = state.get("agent_responses", {})
                agent_responses["analysis"] = analysis_response
                
                return {
                    **state,
                    "agent_responses": agent_responses,
                    "context": {
                        **state.get("context", {}),
                        "analysis_completed": True
                    }
                }
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                agent_responses = state.get("agent_responses", {})
                agent_responses["analysis"] = f"Analysis error: {str(e)}"
                return {**state, "agent_responses": agent_responses}
        
        def synthesis_node(state: SystemState) -> SystemState:
            """Synthesize final response"""
            intent = state["intent"]
            query = state["query"]
            agent_responses = state.get("agent_responses", {})
            knowledge_sources = state.get("knowledge_sources", [])
            
            # Build comprehensive response
            response_parts = []
            
            # Add main content based on intent
            if intent == "information_retrieval":
                if "knowledge" in agent_responses:
                    response_parts.append("📚 **İlgili Bilgiler:**")
                    response_parts.append(agent_responses["knowledge"])
            
            elif intent == "analysis":
                if "analysis" in agent_responses:
                    response_parts.append("🔍 **Detaylı Analiz:**")
                    response_parts.append(agent_responses["analysis"])
                
                if "knowledge" in agent_responses:
                    response_parts.append("\n📖 **Kaynak Bilgiler:**")
                    response_parts.append(agent_responses["knowledge"])
            
            else:  # general_query, comparison, summarization
                # Combine all available responses
                if "knowledge" in agent_responses:
                    response_parts.append("📚 **Bilgi Bankası:**")
                    response_parts.append(agent_responses["knowledge"])
                
                if "analysis" in agent_responses:
                    response_parts.append("\n🔍 **Analiz:**")
                    response_parts.append(agent_responses["analysis"])
            
            # Add sources if available
            if knowledge_sources:
                response_parts.append(f"\n📄 **Kaynaklar:** {', '.join(set(knowledge_sources))}")
            
            final_response = "\n\n".join(response_parts) if response_parts else "Üzgünüm, bu konuda yeterli bilgi bulunamadı."
            
            # Calculate confidence score
            confidence = self._calculate_confidence(state)
            
            return {
                **state,
                "final_response": final_response,
                "confidence_score": confidence,
                "processing_time": (datetime.now() - datetime.fromisoformat(state.get("metadata", {}).get("start_time", datetime.now().isoformat()))).total_seconds()
            }
        
        def route_by_intent(state: SystemState) -> str:
            """Route based on classified intent"""
            intent = state["intent"]
            
            if intent in ["information_retrieval", "general_query"]:
                return "knowledge_only"
            elif intent in ["analysis", "comparison", "summarization"]:
                return "knowledge_and_analysis"
            else:
                return "knowledge_only"
        
        # Create workflow
        workflow = StateGraph(SystemState)
        
        # Add nodes
        workflow.add_node("intent_classification", intent_classification_node)
        workflow.add_node("knowledge_retrieval", knowledge_retrieval_node)
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("synthesis", synthesis_node)
        
        # Set entry point
        workflow.set_entry_point("intent_classification")
        
        # Add edges
        workflow.add_edge("intent_classification", "knowledge_retrieval")
        
        # Conditional routing after knowledge retrieval
        workflow.add_conditional_edges(
            "knowledge_retrieval",
            route_by_intent,
            {
                "knowledge_only": "synthesis",
                "knowledge_and_analysis": "analysis"
            }
        )
        
        workflow.add_edge("analysis", "synthesis")
        workflow.add_edge("synthesis", "__end__")
        
        # Add checkpointer for state persistence
        checkpointer = SqliteSaver.from_conn_string("enterprise_rag_state.db")
        self.graph = workflow.compile(checkpointer=checkpointer)
        
        logger.info("LangGraph workflow initialized")
    
    def _calculate_confidence(self, state: SystemState) -> float:
        """Calculate response confidence score"""
        base_confidence = 0.5
        
        # Boost confidence if we have knowledge sources
        if state.get("knowledge_sources"):
            base_confidence += 0.2
        
        # Boost if analysis was performed
        if "analysis" in state.get("agent_responses", {}):
            base_confidence += 0.2
        
        # Check response quality indicators
        final_response = state.get("final_response", "")
        if len(final_response) > 100:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    async def ingest_documents(self, directory_path: str, file_patterns: List[str] = None):
        """Batch document ingestion"""
        if file_patterns is None:
            file_patterns = ["*.txt", "*.pdf", "*.md", "*.docx"]
        
        logger.info(f"Starting document ingestion from {directory_path}")
        
        all_documents = []
        
        for pattern in file_patterns:
            try:
                loader = DirectoryLoader(directory_path, glob=pattern)
                documents = loader.load()
                all_documents.extend(documents)
                logger.info(f"Loaded {len(documents)} documents with pattern {pattern}")
            except Exception as e:
                logger.error(f"Error loading documents with pattern {pattern}: {e}")
        
        if not all_documents:
            logger.warning("No documents found to ingest")
            return
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config["embeddings"]["chunk_size"],
            chunk_overlap=self.config["embeddings"]["chunk_overlap"],
            length_function=len
        )
        
        splits = text_splitter.split_documents(all_documents)
        logger.info(f"Created {len(splits)} document chunks")
        
        # Create or update vectorstore
        if self.vectorstore is None:
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory=self.config["vectorstore"]["persist_directory"],
                collection_name=self.config["vectorstore"]["collection_name"]
            )
            logger.info("New vectorstore created")
        else:
            # Add to existing vectorstore
            self.vectorstore.add_documents(splits)
            logger.info("Documents added to existing vectorstore")
        
        # Persist
        self.vectorstore.persist()
        
        # Update agents with new vectorstore
        self._init_agents()
        
        logger.info(f"Document ingestion completed. Total documents: {len(all_documents)}, Total chunks: {len(splits)}")
    
    async def query_system(self, query: str, user_id: str = "default", session_id: str = None) -> Dict:
        """Main query interface"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        start_time = datetime.now()
        
        initial_state = {
            "session_id": session_id,
            "user_id": user_id,
            "query": query,
            "intent": "",
            "context": {},
            "knowledge_sources": [],
            "agent_responses": {},
            "final_response": "",
            "confidence_score": 0.0,
            "processing_time": 0.0,
            "metadata": {
                "start_time": start_time.isoformat(),
                "query_length": len(query)
            }
        }
        
        try:
            # Configure session for state persistence
            config = {"configurable": {"thread_id": session_id}}
            
            # Run the graph
            result = self.graph.invoke(initial_state, config=config)
            
            logger.info(f"Query processed successfully in {result['processing_time']:.2f}s")
            
            return {
                "success": True,
                "session_id": session_id,
                "query": query,
                "response": result["final_response"],
                "confidence_score": result["confidence_score"],
                "processing_time": result["processing_time"],
                "intent": result["intent"],
                "sources": result["knowledge_sources"],
                "metadata": result["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "session_id": session_id
            }
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        stats = {
            "vectorstore_stats": {},
            "performance_stats": {},
            "configuration": self.config
        }
        
        if self.vectorstore:
            try:
                # Get vectorstore statistics
                collection = self.vectorstore._collection
                stats["vectorstore_stats"] = {
                    "total_documents": collection.count(),
                    "collection_name": collection.name,
                    "embedding_dimension": len(self.embeddings.embed_query("test")) if self.embeddings else "unknown"
                }
            except:
                stats["vectorstore_stats"] = {"error": "Could not retrieve vectorstore stats"}
        
        # Performance stats from callback
        if hasattr(self.callback_handler, 'operations'):
            operations = self.callback_handler.operations
            if operations:
                total_time = sum(op["duration"] for op in operations)
                avg_time = total_time / len(operations)
                stats["performance_stats"] = {
                    "total_operations": len(operations),
                    "average_duration": avg_time,
                    "total_processing_time": total_time
                }
        
        return stats

# Enterprise-level utilities
class EnterpriseMonitoring:
    """Monitoring and analytics for enterprise RAG"""
    
    def __init__(self, db_path: str = "enterprise_monitoring.db"):
        import sqlite3
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize monitoring database"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                session_id TEXT,
                user_id TEXT,
                query TEXT,
                intent TEXT,
                confidence_score REAL,
                processing_time REAL,
                success BOOLEAN,
                sources_count INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_name TEXT,
                metric_value REAL,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_query(self, query_result: Dict):
        """Log query for analytics"""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO query_logs 
            (timestamp, session_id, user_id, query, intent, confidence_score, 
             processing_time, success, sources_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            query_result.get("session_id"),
            query_result.get("user_id", "unknown"),
            query_result.get("query"),
            query_result.get("intent"),
            query_result.get("confidence_score", 0.0),
            query_result.get("processing_time", 0.0),
            query_result.get("success", False),
            len(query_result.get("sources", []))
        ))
        
        conn.commit()
        conn.close()
    
    def get_analytics(self, days: int = 7) -> Dict:
        """Get system analytics"""
        import sqlite3
        from datetime import timedelta
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Query statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_queries,
                AVG(confidence_score) as avg_confidence,
                AVG(processing_time) as avg_processing_time,
                COUNT(CASE WHEN success = 1 THEN 1 END) as successful_queries
            FROM query_logs 
            WHERE timestamp > ?
        """, (cutoff_date,))
        
        query_stats = cursor.fetchone()
        
        # Intent distribution
        cursor.execute("""
            SELECT intent, COUNT(*) as count
            FROM query_logs 
            WHERE timestamp > ?
            GROUP BY intent
            ORDER BY count DESC
        """, (cutoff_date,))
        
        intent_distribution = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "period_days": days,
            "total_queries": query_stats[0] or 0,
            "average_confidence": query_stats[1] or 0.0,
            "average_processing_time": query_stats[2] or 0.0,
            "success_rate": (query_stats[3] or 0) / (query_stats[0] or 1),
            "intent_distribution": intent_distribution
        }

# FastAPI Web Interface
class EnterpriseRAGAPI:
    """FastAPI interface for Enterprise RAG"""
    
    def __init__(self, rag_system: EnterpriseRAGSystem, monitoring: EnterpriseMonitoring):
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        from fastapi.responses import JSONResponse
        
        self.app = FastAPI(title="Enterprise RAG API", version="1.0.0")
        self.rag_system = rag_system
        self.monitoring = monitoring
        
        class QueryRequest(BaseModel):
            query: str
            user_id: str = "anonymous"
            session_id: Optional[str] = None
        
        class IngestRequest(BaseModel):
            directory_path: str
            file_patterns: Optional[List[str]] = None
        
        @self.app.post("/query")
        async def query_endpoint(request: QueryRequest):
            """Main query endpoint"""
            try:
                result = await self.rag_system.query_system(
                    query=request.query,
                    user_id=request.user_id,
                    session_id=request.session_id
                )
                
                # Log for monitoring
                self.monitoring.log_query(result)
                
                return JSONResponse(content=result)
                
            except Exception as e:
                logger.error(f"API query error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/ingest")
        async def ingest_endpoint(request: IngestRequest):
            """Document ingestion endpoint"""
            try:
                await self.rag_system.ingest_documents(
                    directory_path=request.directory_path,
                    file_patterns=request.file_patterns
                )
                
                return {"success": True, "message": "Documents ingested successfully"}
                
            except Exception as e:
                logger.error(f"API ingest error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/stats")
        async def stats_endpoint():
            """System statistics endpoint"""
            try:
                system_stats = self.rag_system.get_system_stats()
                analytics = self.monitoring.get_analytics()
                
                return {
                    "system_stats": system_stats,
                    "analytics": analytics
                }
                
            except Exception as e:
                logger.error(f"API stats error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Main demo function
async def enterprise_demo():
    """Comprehensive enterprise demo"""
    print("🏢 Enterprise RAG System Demo")
    print("=" * 60)
    
    # Initialize system
    rag_system = EnterpriseRAGSystem()
    monitoring = EnterpriseMonitoring()
    
    # Sample document ingestion
    print("\n📚 Document Ingestion Phase")
    print("-" * 30)
    
    # Create sample documents directory (you would replace this with real documents)
    sample_docs_dir = "./sample_enterprise_docs"
    os.makedirs(sample_docs_dir, exist_ok=True)
    
    # Create sample documents
    sample_docs = {
        "company_policy.txt": """
        Company Policy Document
        
        Our company values innovation, collaboration, and customer satisfaction.
        We have strict data privacy policies and security protocols.
        All employees must complete annual training on cybersecurity.
        """,
        "product_manual.txt": """
        Product Manual
        
        Our flagship AI product uses advanced machine learning algorithms.
        It provides real-time analytics and predictive insights.
        The system supports both on-premise and cloud deployments.
        Technical support is available 24/7 for enterprise customers.
        """,
        "financial_report.txt": """
        Q4 Financial Report
        
        Revenue increased 25% year-over-year.
        Our AI division contributed 40% of total revenue.
        Customer retention rate is 95%.
        We plan to expand into European markets next year.
        """
    }
    
    for filename, content in sample_docs.items():
        with open(f"{sample_docs_dir}/{filename}", "w") as f:
            f.write(content)
    
    # Ingest documents
    await rag_system.ingest_documents(sample_docs_dir)
    
    # Demo queries
    print("\n🤖 Interactive Query Demo")
    print("-" * 30)
    
    test_queries = [
        "What is our company policy on data privacy?",
        "Tell me about our AI product features",
        "Analyze our financial performance in Q4",
        "Compare our customer retention with industry standards",
        "What are the key highlights from all our documents?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        
        result = await rag_system.query_system(
            query=query,
            user_id=f"demo_user_{i}",
            session_id=f"demo_session_{i}"
        )
        
        if result["success"]:
            print(f"✅ Response (Confidence: {result['confidence_score']:.2f}):")
            print(f"   {result['response'][:200]}...")
            print(f"📊 Processing time: {result['processing_time']:.2f}s")
            print(f"🎯 Intent: {result['intent']}")
            print(f"📄 Sources: {len(result['sources'])} documents")
        else:
            print(f"❌ Error: {result['error']}")
        
        # Log for monitoring
        monitoring.log_query(result)
        
        print("-" * 50)
    
    # System analytics
    print("\n📈 System Analytics")
    print("-" * 30)
    
    analytics = monitoring.get_analytics(days=1)
    system_stats = rag_system.get_system_stats()
    
    print(f"Total queries processed: {analytics['total_queries']}")
    print(f"Average confidence score: {analytics['average_confidence']:.3f}")
    print(f"Average processing time: {analytics['average_processing_time']:.3f}s")
    print(f"Success rate: {analytics['success_rate']:.2%}")
    print(f"Intent distribution: {analytics['intent_distribution']}")
    
    if system_stats['vectorstore_stats']:
        print(f"Knowledge base size: {system_stats['vectorstore_stats'].get('total_documents', 'unknown')} documents")
    
    # Cleanup demo files
    import shutil
    if os.path.exists(sample_docs_dir):
        shutil.rmtree(sample_docs_dir)
    
    print("\n✨ Enterprise RAG Demo completed successfully!")

# Production deployment example
def create_production_app():
    """Create production-ready FastAPI app"""
    
    # Load configuration from environment
    config_path = os.getenv("RAG_CONFIG_PATH", "production_config.json")
    
    # Initialize core systems
    rag_system = EnterpriseRAGSystem(config_path)
    monitoring = EnterpriseMonitoring()
    api = EnterpriseRAGAPI(rag_system, monitoring)
    
    # Add middleware for CORS, rate limiting, etc.
    from fastapi.middleware.cors import CORSMiddleware
    
    api.app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return api.app

if __name__ == "__main__":
    # Run demo
    asyncio.run(enterprise_demo())
```

---

## 🚀 Production Deployment Guide

### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p ./chroma_storage ./logs

# Set environment variables
ENV PYTHONPATH=/app
ENV RAG_CONFIG_PATH=/app/production_config.json

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:create_production_app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  rag-api:
    build: ..
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RAG_CONFIG_PATH=/app/config/production_config.json
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./chroma_storage:/app/chroma_storage
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rag_monitoring
      POSTGRES_USER: rag_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - rag-api
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### Production Configuration
```json
{
  "llm": {
    "model": "gpt-4",
    "temperature": 0.1,
    "max_tokens": 4000,
    "request_timeout": 30
  },
  "embeddings": {
    "model": "text-embedding-ada-002",
    "chunk_size": 1500,
    "chunk_overlap": 300,
    "batch_size": 100
  },
  "vectorstore": {
    "persist_directory": "./chroma_storage",
    "collection_name": "production_knowledge",
    "distance_metric": "cosine"
  },
  "system": {
    "max_retries": 3,
    "timeout": 60,
    "enable_caching": true,
    "cache_ttl": 3600,
    "max_concurrent_requests": 50,
    "enable_monitoring": true,
    "log_level": "INFO"
  },
  "security": {
    "enable_auth": true,
    "rate_limit": {
      "requests_per_minute": 100,
      "burst_size": 20
    },
    "cors_origins": ["https://yourcompany.com"],
    "api_key_required": true
  }
}
```

---

## 📊 Monitoring ve Analytics

### Comprehensive Monitoring System
```python
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import time

class PrometheusMetrics:
    """Prometheus metrics for RAG system"""
    
    def __init__(self):
        # Counters
        self.query_total = Counter('rag_queries_total', 'Total queries processed')
        self.error_total = Counter('rag_errors_total', 'Total errors', ['error_type'])
        
        # Histograms
        self.query_duration = Histogram('rag_query_duration_seconds', 'Query processing time')
        self.confidence_score = Histogram('rag_confidence_score', 'Response confidence scores')
        
        # Gauges
        self.active_sessions = Gauge('rag_active_sessions', 'Active user sessions')
        self.vectorstore_size = Gauge('rag_vectorstore_documents', 'Number of documents in vectorstore')

# Grafana Dashboard JSON
grafana_dashboard = {
    "dashboard": {
        "title": "Enterprise RAG System",
        "panels": [
            {
                "title": "Query Rate",
                "type": "graph",
                "targets": [{"expr": "rate(rag_queries_total[5m])"}]
            },
            {
                "title": "Average Response Time",
                "type": "stat",
                "targets": [{"expr": "avg(rag_query_duration_seconds)"}]
            },
            {
                "title": "Error Rate",
                "type": "graph", 
                "targets": [{"expr": "rate(rag_errors_total[5m])"}]
            },
            {
                "title": "Confidence Score Distribution",
                "type": "histogram",
                "targets": [{"expr": "rag_confidence_score"}]
            }
        ]
    }
}
```

---

## 🎯 Son Özet ve Best Practices

### ✅ **Bu Seride Öğrendikleriniz:**

#### **Temeller:**
- LangChain ekosisteminin tüm bileşenleri
- RAG mimarisinin derinlemesine analizi
- ChromaDB ile vektör veritabanı yönetimi
- LangGraph ile karmaşık workflow tasarımı

#### **İleri Seviye:**
- Multi-agent sistemler
- State management ve persistence
- Error handling ve recovery patterns
- Production deployment stratejileri

#### **Enterprise Çözümler:**
- Ölçeklenebilir mimari tasarımı
- Monitoring ve analytics
- Security ve performance optimization
- Real-world integration patterns

### 🚀 **Production Checklist:**

#### **Güvenlik:**
- [ ] API key management
- [ ] Rate limiting implementation
- [ ] CORS configuration
- [ ] Authentication/authorization
- [ ] Input validation
- [ ] Audit logging

#### **Performance:**
- [ ] Caching strategies
- [ ] Database optimization
- [ ] Async processing
- [ ] Load balancing
- [ ] Resource monitoring
- [ ] Scalability testing

#### **Monitoring:**
- [ ] Metrics collection
- [ ] Alerting rules
- [ ] Log aggregation
- [ ] Performance dashboards
- [ ] Error tracking
- [ ] Usage analytics

#### **Reliability:**
- [ ] Error handling
- [ ] Retry mechanisms
- [ ] Circuit breakers
- [ ] Health checks
- [ ] Backup strategies
- [ ] Disaster recovery

### 🎓 **Öğrenme Yol Haritası:**

#### **Başlangıç Seviyesi (1-2 hafta):**
1. LangChain temellerini öğrenin
2. Basit RAG sistemi kurun
3. ChromaDB ile deneyim kazanın
4. İlk chatbot'unuzu yapın

#### **Orta Seviye (3-4 hafta):**
1. LangGraph workflow'ları tasarlayın
2. Multi-agent sistemler oluşturun
3. Custom tool'lar geliştirin
4. Performance optimization yapın

#### **İleri Seviye (5-8 hafta):**
1. Enterprise-grade sistem tasarlayın
2. Production deployment yapın
3. Monitoring ve analytics ekleyin
4. Security best practices uygulayın

### 📚 **Ek Kaynaklar:**

#### **Dokümantasyonlar:**
- [LangChain Documentation](https://docs.langchain.com)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

#### **Pratik Projeler:**
1. **Personal Knowledge Assistant**: Kişisel dokümanlarınız için RAG
2. **Company Wiki Bot**: Şirket bilgileri için chatbot
3. **Research Assistant**: Akademik makale analizi
4. **Customer Support Bot**: Müşteri hizmetleri otomasyonu
5. **Document QA System**: Legal/teknik doküman analizi

#### **Gelişmiş Konular:**
- Multi-modal RAG (text + images)
- Real-time streaming responses
- Federated learning integration
- Edge deployment strategies
- Custom embedding models

---

## 🌟 Kapanış

Bu kapsamlı dokümantasyon serisi ile LangChain, RAG, ChromaDB ve LangGraph ekosisteminin derinliklerine indik. Temelden production-ready enterprise çözümlerine kadar her seviyeyi kapsadık.

### **Önemli Hatırlatmalar:**

1. **Practice Makes Perfect**: Teorik bilgi önemli ama pratik deneyim daha değerli
2. **Start Small**: Küçük projelerle başlayıp kademeli olarak büyütün
3. **Stay Updated**: AI alanı hızla gelişiyor, güncel kalın
4. **Community**: LangChain topluluğu çok aktif, sorularınızı çekinmeden sorun
5. **Ethics**: AI'nın etik kullanımını her zaman göz önünde bulundurun

### **Son Sözler:**

RAG teknolojisi, AI'nın pratik uygulamalarında devrim yaratıyor. Bu teknolojileri öğrenerek, gerçek dünya problemlerine etkili çözümler geliştirebilirsiniz. Unutmayın ki en iyi öğrenme yöntemi, öğrendiklerinizi gerçek projelerde uygulamaktır.

Başarılar dilerim! 🚀

---

**📞 Destek ve İletişim:**
- GitHub: [LangChain Repository](https://github.com/langchain-ai/langchain)
- Discord: LangChain Community
- Stack Overflow: #langchain tag'i
- LinkedIn: AI/ML communities

**🔄 Güncellemeler:**
Bu dokümantasyon düzenli olarak güncellenmektedir. Yeni özellikler ve best practice'ler eklendikçe revize edilecektir.

---

*Bu dokümantasyon tamamen eğitim amaçlı hazırlanmıştır. Production ortamında kullanım öncesinde güvenlik ve performans testleri yapılması önerilir.*# LangChain ve RAG Ekosistemi - Bölüm 5: Tam Entegrasyon ve Production

## 🏗️ Kapsamlı RAG + LangGraph Sistemi

### Sistem Mimarisi

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Kullanıcı     │───▶│    LangGraph     │───▶│    ChromaDB     │
│   Interface     │    │    Workflow      │    │   VectorStore   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          ▲
                              ▼                          │
                      ┌──────────────────┐              │
                      │    LangChain     │              │
                      │     Agents       │              │
                      └──────────────────┘              │
                              │                          │
                              ▼                          │
                      ┌──────────────────┐              │
                      │      LLMs        │              │
                      │ (OpenAI/Claude)  │              │
                      └──────────────────┘              │
                              │                          │
                              ▼                          │
                      ┌──────────────────┐              │
                      │   Knowledge      │──────────────┘
                      │   Processing     │
                      └──────────────────┘
```

### Master Implementation
```python
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, TypedDict
import logging
import json
import os
from pathlib import Path

# LangChain imports
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import CallbackManager
from langchain.callbacks.base import BaseCallbackHandler

# LangGraph imports
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver

# ChromaDB imports
import chromadb
from chromadb.config import Settings

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemState(TypedDict):
    """Sistem geneli state"""
    session_id: str
    user_id: str
    query: str
    intent: str
    context: Dict
    knowledge_sources: List[str]
    agent_responses: Dict[str, str]
    final_response: str
    confidence_score: float
    processing_time: float
    metadata: Dict

class CustomCallbackHandler(BaseCallbackHandler):
    """Performance ve logging callback"""
    
    def __init__(self):
        self.start_time = None
        self.operations = []
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = datetime.now()
        logger.info(f"LLM started with {len(prompts)} prompts")
    
    def on_llm_end(self, response, **kwargs):
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"LLM completed in {duration:.2f}s")
            self.operations.append({"operation": "llm", "duration": duration})
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        logger.info(f"Tool started: {serialized.get('name', 'unknown')}")
    
    def on_tool_end(self, output, **kwargs):
        logger.info(f"Tool completed")

class EnterpriseRAGSystem:
    """Enterprise-grade RAG System"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.callback_handler = CustomCallbackHandler()
        
        # Initialize components
        self._init_llm()
        self._init_embeddings()
        self._init_vectorstore()
        self._init_agents()
        self._init_graph()
        
        logger.info("Enterprise RAG System initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Konfigürasyon yükle"""
        default_config = {
            "llm": {
                "model": "gpt-3.5-turbo-instruct",
                "temperature": 0.2,
                "max_tokens": 2000
            },
            "embeddings": {
                "model": "text-embedding-ada-002",
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "vectorstore": {
                "persist_directory": "./enterprise_chroma",
                "collection_name": "enterprise_knowledge"
            },
            "system": {
                "max_retries": 3,
                "timeout": 30,
                "enable_caching": True
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Deep merge configurations
            self._deep_update(default_config, user_config)
        
        return default_config
    
    def _deep_update(self, base_dict, update_dict):
        """Deep dictionary update"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def _init_llm(self):
        """LLM initialization"""
        self.llm = OpenAI(
            temperature=self.config["llm"]["temperature"],
            max_tokens=self.config["llm"]["max_tokens"],
            callback_manager=CallbackManager([self.callback_handler])
        )
        logger.info("LLM initialized")
    
    def _init_embeddings(self):
        """Embeddings initialization"""
        self.embeddings = OpenAIEmbeddings(
            model=self.config["embeddings"]["model"]
        )
        logger.info("Embeddings initialized")
    
    def _init_vectorstore(self):
        """Vector store initialization"""
        persist_dir = self.config["vectorstore"]["persist_directory"]
        
        if os.path.exists(persist_dir):
            self.vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self.embeddings,
                collection_name=self.config["vectorstore"]["collection_name"]
            )
            logger.info("Existing vectorstore loaded")
        else:
            self.vectorstore = None
            logger.info("No existing vectorstore found")
    
    def _init_agents(self):
        """Specialized agents initialization"""
        
        # Knowledge Agent
        class KnowledgeRetrievalTool(BaseTool):
            name = "knowledge_retrieval"
            description = "Retrieves relevant information from knowledge base"
            
            def __init__(self, vectorstore, embeddings):
                super().__init__()
                self.vectorstore = vectorstore
                self.embeddings = embeddings
            
            def _run(self, query: str) -> str:
                if not self.vectorstore:
                    return "Knowledge base not available"
                
                docs = self.vectorstore.similarity_search(query, k=3)
                return "\n\n".join([doc.page_content for doc in docs])
            
            async def _arun(self, query: str) -> str:
                return self._run(query)
        
        # Analysis Agent
        class AnalysisTool(BaseTool):
            name = "analysis_tool"
            description = "Performs detailed analysis on given data"
            
            def _run(self, data: str) -> str:
                # Simulated analysis
                lines = data.split('\n')
                word_count = len(data.split())
                
                analysis = f"""
                Analysis Results:
                - Document lines: {len(lines)}
                - Word count: {word_count}
                - Key topics detected: {self._extract_topics(data)}
                - Sentiment: {self._detect_sentiment(data)}
                """
                return analysis
            
            def _extract_topics(self, text: str) -> List[str]:
                # Simple topic extraction
                keywords = ["python", "ai", "machine learning", "data", "technology"]
                found_topics = [kw for kw in keywords if kw.lower() in text.lower()]
                return found_topics[:3]
            
            def _detect_sentiment(self, text: str) -> str:
                positive_words = ["good", "excellent", "great", "amazing"]
                negative_words = ["bad", "terrible", "awful", "poor"]
                
                pos_count = sum(1 for word in positive_words if word in text.lower())
                neg_count = sum(1 for word in negative_words if word in text.lower())
                
                if pos_count > neg_count:
                    return "positive"
                elif neg_count > pos_count:
                    return "negative"
                return "neutral"
            
            async def _arun(self, data: str) -> str:
                return self._run(data)
        
        # Initialize tools
        self.knowledge_tool = KnowledgeRetrievalTool(self.vectorstore, self.embeddings)
        self.analysis_tool = AnalysisTool()
        
        # Create agents
        self.knowledge_agent = initialize_agent(
            [self.knowledge_tool],
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        self.analysis_agent = initialize_agent(
            [self.analysis_tool],
            self.llm, 
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        logger.info("Agents initialized")
    
    def _init_graph(self):
        """LangGraph workflow initialization"""
        
        def intent_classification_node(state: SystemState) -> SystemState:
            """Classify user intent"""
            query = state["query"].lower()
            
            if any(word in query for word in ["search", "find", "lookup", "what is"]):
                intent = "information_retrieval"
            elif any(word in query for word in ["analyze", "analysis", "examine"]):
                intent = "analysis"
            elif any(word in query for word in ["compare", "difference", "versus"]):
                intent = "comparison"
            elif any