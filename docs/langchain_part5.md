# LangChain ve RAG Ekosistemi - Bölüm 5: Tam Entegrasyon ve Production

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