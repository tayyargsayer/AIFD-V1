# LangChain ve RAG Ekosistemi - Bölüm 4: LangGraph ve Complex Workflows

## 🌐 LangGraph Nedir?

### Basit Anlatım
LangGraph'ı **akıllı şirket organizasyon şeması** olarak düşünün. Geleneksel Chain'ler tek yönlü çalışırken (A→B→C), LangGraph karmaşık karar ağaçları ve döngüler oluşturabilir.

### Analoji: **Şirket Karar Süreci**
```
Geleneksel Chain:     Problem → Analiz → Karar → Uygulama
                      (Tek yön, geri dönüş yok)

LangGraph:           Problem → Analiz ⟷ Araştırma
                            ↕        ↕
                     İnsan Onayı ← Karar → Revizyon
                            ↓        ↗
                        Uygulama → Sonuç Kontrolü
```

### LangGraph'ın Avantajları
- **🔄 Döngüsel yapı**: Geri bildirim ve revizyonlar
- **🤝 Multi-agent**: Birden fazla AI agent'ın koordinasyonu
- **🧠 State management**: Durumları takip etme
- **⚡ Conditional routing**: Koşullu yönlendirme
- **🔀 Parallel execution**: Paralel işlem desteği

---

## 🛠️ LangGraph Kurulum ve Temel Kavramlar

### Kurulum
```bash
pip install langgraph langchain openai
```

### Temel Kavramlar

#### 1. **Node (Düğüm)**
Her node bir işlevi temsil eder:
```python
def analyze_node(state):
    """Analiz yapan node"""
    return {"analysis_result": "Data analyzed successfully"}

def decision_node(state):
    """Karar veren node"""
    if state["analysis_result"] == "positive":
        return {"next_action": "proceed"}
    else:
        return {"next_action": "revise"}
```

#### 2. **Edge (Kenar)**
Node'lar arasındaki bağlantılar:
```python
# Basit edge: her zaman B'ye git
graph.add_edge("node_a", "node_b")

# Conditional edge: koşula göre yönlendirme
def route_decision(state):
    if state["confidence"] > 0.8:
        return "approve"
    else:
        return "review"

graph.add_conditional_edges(
    "decision_node",
    route_decision,
    {
        "approve": "final_node",
        "review": "human_review_node"
    }
)
```

#### 3. **State (Durum)**
Tüm node'lar arasında paylaşılan veri:
```python
from typing import TypedDict

class GraphState(TypedDict):
    user_input: str
    processed_data: str
    confidence_score: float
    iterations: int
    final_result: str
```

---

## 🚀 İlk LangGraph Uygulaması

### Basit Örnek: Araştırma Asistanı
```python
from langgraph.graph import StateGraph
from typing import TypedDict
import json

# State tanımı
class ResearchState(TypedDict):
    question: str
    search_results: list
    analysis: str
    final_answer: str
    iteration_count: int

def search_node(state: ResearchState) -> ResearchState:
    """Web araması yapan node"""
    question = state["question"]
    
    # Simülasyon: gerçekte web araması yapılır
    fake_results = [
        f"Result 1 for {question}",
        f"Result 2 for {question}", 
        f"Result 3 for {question}"
    ]
    
    return {
        **state,
        "search_results": fake_results,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def analyze_node(state: ResearchState) -> ResearchState:
    """Sonuçları analiz eden node"""
    results = state["search_results"]
    
    # Basit analiz simülasyonu
    analysis = f"Analyzed {len(results)} search results for: {state['question']}"
    
    return {
        **state,
        "analysis": analysis
    }

def synthesize_node(state: ResearchState) -> ResearchState:
    """Final cevabı oluşturan node"""
    question = state["question"]
    analysis = state["analysis"]
    
    final_answer = f"Based on the analysis: {analysis}, here's the answer to '{question}'"
    
    return {
        **state,
        "final_answer": final_answer
    }

def should_continue(state: ResearchState) -> str:
    """Devam edilmeli mi karar veren fonksiyon"""
    iteration_count = state.get("iteration_count", 0)
    
    if iteration_count < 2:
        return "continue"
    else:
        return "end"

# Graph oluştur
workflow = StateGraph(ResearchState)

# Node'ları ekle
workflow.add_node("search", search_node)
workflow.add_node("analyze", analyze_node)
workflow.add_node("synthesize", synthesize_node)

# Entry point
workflow.set_entry_point("search")

# Edge'leri ekle
workflow.add_edge("search", "analyze")

# Conditional edge
workflow.add_conditional_edges(
    "analyze",
    should_continue,
    {
        "continue": "search",  # Daha fazla arama yap
        "end": "synthesize"    # Final cevabı oluştur
    }
)

# Finish edge
workflow.add_edge("synthesize", "__end__")

# Graph'ı compile et
research_graph = workflow.compile()

# Kullanım
def run_research(question: str):
    initial_state = {
        "question": question,
        "search_results": [],
        "analysis": "",
        "final_answer": "",
        "iteration_count": 0
    }
    
    result = research_graph.invoke(initial_state)
    return result

# Test
result = run_research("What is LangGraph?")
print("Final Result:", result["final_answer"])
```

---

## 🤖 Multi-Agent Sistemler

### Agent Türleri ve Roller

#### 1. **Researcher Agent**
```python
from langchain.agents import initialize_agent, AgentType
from langchain.tools import DuckDuckGoSearchRun
from langchain.llms import OpenAI

class ResearcherAgent:
    def __init__(self):
        self.llm = OpenAI(temperature=0.2)
        self.search_tool = DuckDuckGoSearchRun()
        self.tools = [self.search_tool]
        
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    
    def research(self, topic):
        prompt = f"""
        Aşağıdaki konu hakkında kapsamlı araştırma yap:
        Konu: {topic}
        
        Araştırman şunları içermeli:
        1. Temel tanım
        2. Ana özellikler
        3. Kullanım alanları
        4. Güncel gelişmeler
        """
        
        return self.agent.run(prompt)

class AnalystAgent:
    def __init__(self):
        self.llm = OpenAI(temperature=0.1)
    
    def analyze(self, research_data, focus_area=None):
        prompt = f"""
        Aşağıdaki araştırma verilerini analiz et:
        {research_data}
        
        Odak alanı: {focus_area or 'Genel analiz'}
        
        Analizin şunları içermeli:
        1. Ana bulgular
        2. Güçlü yönler
        3. Zayıf yönler
        4. Öneriler
        """
        
        return self.llm(prompt)

class WriterAgent:
    def __init__(self):
        self.llm = OpenAI(temperature=0.7)
    
    def write_report(self, analysis_data, target_audience="genel"):
        prompt = f"""
        Aşağıdaki analiz verilerini kullanarak {target_audience} kitlesi için rapor yaz:
        {analysis_data}
        
        Rapor formatı:
        1. Özet
        2. Detaylı Açıklama  
        3. Sonuç ve Öneriler
        
        Ton: Profesyonel ve anlaşılır
        """
        
        return self.llm(prompt)
```

#### 2. **Multi-Agent Workflow**
```python
from typing import TypedDict

class MultiAgentState(TypedDict):
    original_query: str
    research_data: str
    analysis_data: str
    final_report: str
    current_agent: str
    iteration: int

def researcher_node(state: MultiAgentState) -> MultiAgentState:
    """Araştırma agent'ı"""
    researcher = ResearcherAgent()
    research_result = researcher.research(state["original_query"])
    
    return {
        **state,
        "research_data": research_result,
        "current_agent": "researcher",
        "iteration": state.get("iteration", 0) + 1
    }

def analyst_node(state: MultiAgentState) -> MultiAgentState:
    """Analiz agent'ı"""
    analyst = AnalystAgent()
    analysis_result = analyst.analyze(state["research_data"])
    
    return {
        **state,
        "analysis_data": analysis_result,
        "current_agent": "analyst"
    }

def writer_node(state: MultiAgentState) -> MultiAgentState:
    """Yazım agent'ı"""
    writer = WriterAgent()
    final_report = writer.write_report(state["analysis_data"])
    
    return {
        **state,
        "final_report": final_report,
        "current_agent": "writer"
    }

def quality_check_node(state: MultiAgentState) -> MultiAgentState:
    """Kalite kontrol node'u"""
    report = state["final_report"]
    
    # Basit kalite kontrol kriterleri
    quality_score = 0
    if len(report) > 500:
        quality_score += 1
    if "özet" in report.lower():
        quality_score += 1
    if "sonuç" in report.lower():
        quality_score += 1
    
    return {
        **state,
        "quality_score": quality_score
    }

def decide_next_step(state: MultiAgentState) -> str:
    """Sonraki adımı belirle"""
    quality_score = state.get("quality_score", 0)
    iteration = state.get("iteration", 0)
    
    if quality_score >= 2 or iteration >= 3:
        return "finish"
    else:
        return "revise"

# Multi-agent workflow oluştur
multi_agent_workflow = StateGraph(MultiAgentState)

# Agent node'larını ekle
multi_agent_workflow.add_node("researcher", researcher_node)
multi_agent_workflow.add_node("analyst", analyst_node)
multi_agent_workflow.add_node("writer", writer_node)
multi_agent_workflow.add_node("quality_check", quality_check_node)

# Entry point
multi_agent_workflow.set_entry_point("researcher")

# Sequential edges
multi_agent_workflow.add_edge("researcher", "analyst")
multi_agent_workflow.add_edge("analyst", "writer")
multi_agent_workflow.add_edge("writer", "quality_check")

# Conditional edge for revision
multi_agent_workflow.add_conditional_edges(
    "quality_check",
    decide_next_step,
    {
        "revise": "researcher",  # Baştan başla
        "finish": "__end__"      # Bitir
    }
)

# Compile
multi_agent_graph = multi_agent_workflow.compile()

# Kullanım
def run_multi_agent_research(query: str):
    initial_state = {
        "original_query": query,
        "research_data": "",
        "analysis_data": "",
        "final_report": "",
        "current_agent": "",
        "iteration": 0
    }
    
    result = multi_agent_graph.invoke(initial_state)
    return result

# Test
result = run_multi_agent_research("Python vs JavaScript karşılaştırması")
print("Final Report:", result["final_report"])
```

---

## 🧠 State Management ve Persistence

### Gelişmiş State Yönetimi
```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
import sqlite3
from datetime import datetime

class PersistentState(TypedDict):
    session_id: str
    user_id: str
    conversation_history: list
    current_context: str
    preferences: dict
    timestamp: str

def conversation_node(state: PersistentState) -> PersistentState:
    """Konuşma node'u"""
    history = state.get("conversation_history", [])
    
    # Yeni mesajı ekle
    new_message = {
        "timestamp": datetime.now().isoformat(),
        "context": state.get("current_context", ""),
        "processed": True
    }
    
    history.append(new_message)
    
    return {
        **state,
        "conversation_history": history,
        "timestamp": datetime.now().isoformat()
    }

def preference_update_node(state: PersistentState) -> PersistentState:
    """Kullanıcı tercihlerini güncelle"""
    preferences = state.get("preferences", {})
    
    # Konuşma geçmişinden tercihleri öğren
    history = state.get("conversation_history", [])
    if len(history) > 5:
        preferences["experienced_user"] = True
    else:
        preferences["experienced_user"] = False
    
    return {
        **state,
        "preferences": preferences
    }

# SQLite checkpoint saver
checkpointer = SqliteSaver.from_conn_string("workflow_state.db")

# Persistent workflow
persistent_workflow = StateGraph(PersistentState)
persistent_workflow.add_node("conversation", conversation_node)
persistent_workflow.add_node("update_preferences", preference_update_node)

persistent_workflow.set_entry_point("conversation")
persistent_workflow.add_edge("conversation", "update_preferences")
persistent_workflow.add_edge("update_preferences", "__end__")

# Checkpointer ile compile
persistent_graph = persistent_workflow.compile(checkpointer=checkpointer)

# Kullanım - session ile
def run_with_session(user_input: str, session_id: str, user_id: str):
    config = {"configurable": {"thread_id": session_id}}
    
    initial_state = {
        "session_id": session_id,
        "user_id": user_id,
        "current_context": user_input,
        "conversation_history": [],
        "preferences": {},
        "timestamp": datetime.now().isoformat()
    }
    
    result = persistent_graph.invoke(initial_state, config=config)
    return result

# Test with sessions
session1_result = run_with_session("Merhaba", "session_001", "user_123")
session1_result2 = run_with_session("Python öğreniyorum", "session_001", "user_123")

print("Session 1 History:", len(session1_result2["conversation_history"]))
```

---

## 🔄 Advanced Patterns

### 1. **Human-in-the-Loop Pattern**
```python
class HumanInTheLoopState(TypedDict):
    task: str
    ai_proposal: str
    human_feedback: str
    final_decision: str
    requires_human: bool

def ai_analysis_node(state: HumanInTheLoopState) -> HumanInTheLoopState:
    """AI analiz yapar"""
    task = state["task"]
    
    # AI'nın önerisi
    ai_proposal = f"AI önerisi: {task} için en iyi yaklaşım X metodudur."
    
    # Kritik görevler için insan onayı gerekir
    requires_human = "kritik" in task.lower() or "önemli" in task.lower()
    
    return {
        **state,
        "ai_proposal": ai_proposal,
        "requires_human": requires_human
    }

def human_review_node(state: HumanInTheLoopState) -> HumanInTheLoopState:
    """İnsan değerlendirmesi simülasyonu"""
    # Gerçek uygulamada burada insan inputu beklenir
    print(f"İnsan onayı gerekiyor: {state['ai_proposal']}")
    
    # Simülasyon
    human_feedback = "Onaylandı - küçük revizyon gerekli"
    
    return {
        **state,
        "human_feedback": human_feedback
    }

def final_decision_node(state: HumanInTheLoopState) -> HumanInTheLoopState:
    """Final karar"""
    ai_proposal = state["ai_proposal"]
    human_feedback = state.get("human_feedback", "")
    
    if human_feedback:
        final_decision = f"Revize edildi: {ai_proposal} + {human_feedback}"
    else:
        final_decision = ai_proposal
    
    return {
        **state,
        "final_decision": final_decision
    }

def needs_human_approval(state: HumanInTheLoopState) -> str:
    """İnsan onayı gerekli mi?"""
    return "human_review" if state["requires_human"] else "final_decision"

# Human-in-the-loop workflow
hitl_workflow = StateGraph(HumanInTheLoopState)

hitl_workflow.add_node("ai_analysis", ai_analysis_node)
hitl_workflow.add_node("human_review", human_review_node)
hitl_workflow.add_node("final_decision", final_decision_node)

hitl_workflow.set_entry_point("ai_analysis")

hitl_workflow.add_conditional_edges(
    "ai_analysis",
    needs_human_approval,
    {
        "human_review": "human_review",
        "final_decision": "final_decision"
    }
)

hitl_workflow.add_edge("human_review", "final_decision")
hitl_workflow.add_edge("final_decision", "__end__")

hitl_graph = hitl_workflow.compile()
```

### 2. **Error Handling ve Recovery**
```python
class RobustState(TypedDict):
    input_data: str
    processed_data: str
    error_count: int
    last_error: str
    success: bool
    retry_strategy: str

def risky_processing_node(state: RobustState) -> RobustState:
    """Hata çıkabilecek işlem"""
    import random
    
    try:
        # Simüle edilen risky işlem
        if random.random() < 0.3:  # %30 hata şansı
            raise Exception("Processing failed - simulated error")
        
        processed_data = f"Successfully processed: {state['input_data']}"
        
        return {
            **state,
            "processed_data": processed_data,
            "success": True,
            "error_count": 0
        }
        
    except Exception as e:
        error_count = state.get("error_count", 0) + 1
        
        return {
            **state,
            "last_error": str(e),
            "error_count": error_count,
            "success": False
        }

def error_recovery_node(state: RobustState) -> RobustState:
    """Hata recovery stratejisi"""
    error_count = state["error_count"]
    
    if error_count == 1:
        strategy = "simple_retry"
    elif error_count == 2:
        strategy = "alternative_method"
    else:
        strategy = "manual_intervention"
    
    return {
        **state,
        "retry_strategy": strategy
    }

def alternative_processing_node(state: RobustState) -> RobustState:
    """Alternatif işlem yöntemi"""
    # Daha güvenli ama daha yavaş yöntem
    processed_data = f"Alternative processing completed: {state['input_data']}"
    
    return {
        **state,
        "processed_data": processed_data,
        "success": True
    }

def should_retry(state: RobustState) -> str:
    """Retry stratejisini belirle"""
    if state["success"]:
        return "end"
    
    error_count = state["error_count"]
    strategy = state.get("retry_strategy", "")
    
    if error_count >= 3:
        return "fail"
    elif strategy == "alternative_method":
        return "alternative"
    else:
        return "retry"

# Error handling workflow
error_workflow = StateGraph(RobustState)

error_workflow.add_node("processing", risky_processing_node)
error_workflow.add_node("error_recovery", error_recovery_node)
error_workflow.add_node("alternative_processing", alternative_processing_node)

error_workflow.set_entry_point("processing")

error_workflow.add_conditional_edges(
    "processing",
    should_retry,
    {
        "end": "__end__",
        "retry": "error_recovery",
        "alternative": "alternative_processing",
        "fail": "__end__"
    }
)

error_workflow.add_edge("error_recovery", "processing")
error_workflow.add_edge("alternative_processing", "__end__")

robust_graph = error_workflow.compile()

# Test error handling
def test_robust_processing(input_data: str):
    initial_state = {
        "input_data": input_data,
        "processed_data": "",
        "error_count": 0,
        "last_error": "",
        "success": False,
        "retry_strategy": ""
    }
    
    result = robust_graph.invoke(initial_state)
    return result

# Birkaç test
for i in range(3):
    result = test_robust_processing(f"Test data {i+1}")
    print(f"Test {i+1}: Success={result['success']}, Errors={result['error_count']}")
```

---

## 🚀 Gerçek Hayat Projesi: E-ticaret Müşteri Hizmetleri

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List
from datetime import datetime
import json

class CustomerServiceState(TypedDict):
    customer_id: str
    inquiry_type: str
    message: str
    order_info: dict
    sentiment: str
    urgency_level: int
    agent_notes: List[str]
    resolution_steps: List[str]
    escalated: bool
    satisfied: bool
    final_response: str

class OrderLookupAgent:
    def lookup_order(self, customer_id: str, order_id: str = None):
        """Sipariş bilgilerini getir"""
        # Simüle edilmiş sipariş veritabanı
        orders_db = {
            "CUST001": [
                {
                    "order_id": "ORD001",
                    "status": "shipped",
                    "items": ["Laptop", "Mouse"],
                    "total": 15000,
                    "tracking": "TRK123456"
                }
            ],
            "CUST002": [
                {
                    "order_id": "ORD002", 
                    "status": "pending",
                    "items": ["Phone Case"],
                    "total": 50,
                    "tracking": None
                }
            ]
        }
        
        return orders_db.get(customer_id, [])

class SentimentAnalyzer:
    def analyze_sentiment(self, message: str):
        """Müşteri mesajının duygusal tonunu analiz et"""
        negative_words = ["kötü", "berbat", "memnun değil", "şikayet", "problem"]
        positive_words = ["teşekkür", "memnun", "harika", "güzel", "beğendim"]
        urgent_words = ["acil", "hemen", "çok önemli", "kritik"]
        
        message_lower = message.lower()
        
        negative_count = sum(1 for word in negative_words if word in message_lower)
        positive_count = sum(1 for word in positive_words if word in message_lower)
        urgent_count = sum(1 for word in urgent_words if word in message_lower)
        
        if negative_count > positive_count:
            sentiment = "negative"
        elif positive_count > negative_count:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        
        urgency = min(urgent_count + negative_count, 5)  # 0-5 skala
        
        return sentiment, urgency

def intake_node(state: CustomerServiceState) -> CustomerServiceState:
    """Gelen talep analizi"""
    analyzer = SentimentAnalyzer()
    sentiment, urgency = analyzer.analyze_sentiment(state["message"])
    
    # Talep türünü belirle
    message_lower = state["message"].lower()
    if any(word in message_lower for word in ["sipariş", "kargo", "teslimat"]):
        inquiry_type = "order_inquiry"
    elif any(word in message_lower for word in ["iade", "geri dön"]):
        inquiry_type = "return_request"
    elif any(word in message_lower for word in ["ürün", "kalite", "arızalı"]):
        inquiry_type = "product_issue"
    else:
        inquiry_type = "general"
    
    return {
        **state,
        "inquiry_type": inquiry_type,
        "sentiment": sentiment,
        "urgency_level": urgency,
        "agent_notes": [f"Initial analysis: {inquiry_type}, sentiment: {sentiment}"]
    }

def order_lookup_node(state: CustomerServiceState) -> CustomerServiceState:
    """Sipariş bilgilerini getir"""
    lookup_agent = OrderLookupAgent()
    orders = lookup_agent.lookup_order(state["customer_id"])
    
    notes = state.get("agent_notes", [])
    notes.append(f"Found {len(orders)} orders for customer")
    
    return {
        **state,
        "order_info": {"orders": orders, "count": len(orders)},
        "agent_notes": notes
    }

def resolution_node(state: CustomerServiceState) -> CustomerServiceState:
    """Çözüm önerisi oluştur"""
    inquiry_type = state["inquiry_type"]
    order_info = state.get("order_info", {})
    urgency = state["urgency_level"]
    
    resolution_steps = []
    
    if inquiry_type == "order_inquiry":
        if order_info.get("orders"):
            order = order_info["orders"][0]
            if order["status"] == "shipped":
                resolution_steps.append(f"Siparişiniz kargoya verildi. Takip no: {order.get('tracking', 'N/A')}")
            else:
                resolution_steps.append(f"Siparişiniz {order['status']} durumunda")
        else:
            resolution_steps.append("Sipariş bilgisi bulunamadı, manuel kontrol gerekli")
    
    elif inquiry_type == "return_request":
        resolution_steps.append("İade işlemi için gerekli adımlar:")
        resolution_steps.append("1. Ürünü orijinal ambalajında hazırlayın")
        resolution_steps.append("2. İade kodunu alın")
        resolution_steps.append("3. Kargo ile gönderim yapın")
    
    elif inquiry_type == "product_issue":
        resolution_steps.append("Ürün sorunu için:")
        resolution_steps.append("1. Fotoğraf gönderebilir misiniz?")
        resolution_steps.append("2. Garantı kontrol edilecek")
        resolution_steps.append("3. Değişim/onarım seçenekleri sunulacak")
    
    # Yüksek aciliyet durumları
    if urgency >= 4:
        resolution_steps.insert(0, "⚠️ YÜKSEK ÖNCELİK - İnsan desteğine yönlendirilecek")
    
    notes = state.get("agent_notes", [])
    notes.append(f"Generated {len(resolution_steps)} resolution steps")
    
    return {
        **state,
        "resolution_steps": resolution_steps,
        "agent_notes": notes
    }

def escalation_check_node(state: CustomerServiceState) -> CustomerServiceState:
    """Escalation gerekli mi kontrol et"""
    urgency = state["urgency_level"]
    sentiment = state["sentiment"]
    inquiry_type = state["inquiry_type"]
    
    # Escalation kriterleri
    should_escalate = (
        urgency >= 4 or 
        sentiment == "negative" and urgency >= 3 or
        inquiry_type == "product_issue" and sentiment == "negative"
    )
    
    notes = state.get("agent_notes", [])
    notes.append(f"Escalation check: {'Required' if should_escalate else 'Not required'}")
    
    return {
        **state,
        "escalated": should_escalate,
        "agent_notes": notes
    }

def response_generation_node(state: CustomerServiceState) -> CustomerServiceState:
    """Final müşteri yanıtı oluştur"""
    customer_id = state["customer_id"]
    resolution_steps = state["resolution_steps"]
    escalated = state["escalated"]
    sentiment = state["sentiment"]
    
    # Kişiselleştirilmiş yanıt
    greeting = "Merhaba," if sentiment != "negative" else "Merhaba, durumunuz için üzgünüz."
    
    response_parts = [greeting]
    
    if escalated:
        response_parts.append("Talebiniz öncelikli olarak işleme alınmıştır.")
        response_parts.append("Uzman ekibimiz en kısa sürede sizinle iletişime geçecektir.")
    else:
        response_parts.append("Talebinizle ilgili bilgiler:")
        response_parts.extend(resolution_steps)
    
    response_parts.append("Başka bir konuda yardımcı olabileceğimiz bir konu var mı?")
    
    final_response = "\n\n".join(response_parts)
    
    return {
        **state,
        "final_response": final_response,
        "satisfied": True  # Simülasyon için
    }

def requires_escalation(state: CustomerServiceState) -> str:
    """Escalation routing"""
    return "escalated" if state["escalated"] else "standard"

def needs_order_lookup(state: CustomerServiceState) -> str:
    """Sipariş bilgisi gerekli mi?"""
    return "lookup" if state["inquiry_type"] == "order_inquiry" else "resolution"

# Customer service workflow
cs_workflow = StateGraph(CustomerServiceState)

# Node'ları ekle
cs_workflow.add_node("intake", intake_node)
cs_workflow.add_node("order_lookup", order_lookup_node)
cs_workflow.add_node("resolution", resolution_node)
cs_workflow.add_node("escalation_check", escalation_check_node)
cs_workflow.add_node("response_generation", response_generation_node)

# Entry point
cs_workflow.set_entry_point("intake")

# Conditional routing
cs_workflow.add_conditional_edges(
    "intake",
    needs_order_lookup,
    {
        "lookup": "order_lookup",
        "resolution": "resolution"
    }
)

cs_workflow.add_edge("order_lookup", "resolution")
cs_workflow.add_edge("resolution", "escalation_check")

cs_workflow.add_conditional_edges(
    "escalation_check", 
    requires_escalation,
    {
        "escalated": "response_generation",
        "standard": "response_generation"
    }
)

cs_workflow.add_edge("response_generation", "__end__")

# Compile
customer_service_graph = cs_workflow.compile()

class CustomerServiceBot:
    def __init__(self):
        self.graph = customer_service_graph
        self.session_history = {}
    
    def handle_inquiry(self, customer_id: str, message: str):
        """Müşteri talebini işle"""
        initial_state = {
            "customer_id": customer_id,
            "inquiry_type": "",
            "message": message,
            "order_info": {},
            "sentiment": "",
            "urgency_level": 0,
            "agent_notes": [],
            "resolution_steps": [],
            "escalated": False,
            "satisfied": False,
            "final_response": ""
        }
        
        result = self.graph.invoke(initial_state)
        
        # Session history'e kaydet
        if customer_id not in self.session_history:
            self.session_history[customer_id] = []
        
        self.session_history[customer_id].append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": result["final_response"],
            "escalated": result["escalated"],
            "urgency": result["urgency_level"]
        })
        
        return result
    
    def get_analytics(self):
        """Müşteri hizmetleri analitikleri"""
        total_inquiries = sum(len(history) for history in self.session_history.values())
        escalated_count = 0
        urgency_total = 0
        
        for history in self.session_history.values():
            for inquiry in history:
                if inquiry["escalated"]:
                    escalated_count += 1
                urgency_total += inquiry["urgency"]
        
        avg_urgency = urgency_total / total_inquiries if total_inquiries > 0 else 0
        escalation_rate = escalated_count / total_inquiries if total_inquiries > 0 else 0
        
        return {
            "total_inquiries": total_inquiries,
            "escalation_rate": escalation_rate,
            "average_urgency": avg_urgency,
            "unique_customers": len(self.session_history)
        }

# Demo kullanım
def demo_customer_service():
    print("🛒 E-ticaret Müşteri Hizmetleri Demo")
    print("=" * 50)
    
    bot = CustomerServiceBot()
    
    # Test senaryoları
    test_cases = [
        {
            "customer_id": "CUST001",
            "message": "Merhaba, siparişimin durumu nedir? ORD001 numaralı sipariş"
        },
        {
            "customer_id": "CUST002", 
            "message": "Aldığım telefon kılıfı arızalı geldi, çok memnun değilim!"
        },
        {
            "customer_id": "CUST001",
            "message": "Ürünümü iade etmek istiyorum"
        },
        {
            "customer_id": "CUST003",
            "message": "ACİL! Siparişim yarın gelmeli ama hala kargoya verilmemiş!"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test {i}:")
        print(f"Müşteri: {test_case['customer_id']}")
        print(f"Mesaj: {test_case['message']}")
        
        result = bot.handle_inquiry(
            test_case["customer_id"],
            test_case["message"]
        )
        
        print(f"\n🤖 Bot Yanıtı:")
        print(result["final_response"])
        
        print(f"\n📊 Analiz:")
        print(f"- Talep türü: {result['inquiry_type']}")
        print(f"- Duygu durumu: {result['sentiment']}")
        print(f"- Aciliyet: {result['urgency_level']}/5")
        print(f"- Escalate edildi: {'Evet' if result['escalated'] else 'Hayır'}")
        
        print("\n" + "-" * 50)
    
    # Genel analitikler
    print("\n📈 Genel Analitikler:")
    analytics = bot.get_analytics()
    print(f"Toplam talep: {analytics['total_inquiries']}")
    print(f"Escalation oranı: {analytics['escalation_rate']:.2%}")
    print(f"Ortalama aciliyet: {analytics['average_urgency']:.2f}/5")
    print(f"Benzersiz müşteri: {analytics['unique_customers']}")

if __name__ == "__main__":
    demo_customer_service()
```

---

## 🎯 Bölüm 4 Özeti

Bu bölümde öğrendikleriniz:

### ✅ **LangGraph Temelleri:**
- Graph yapısı ve node/edge kavramları
- State management sistemleri
- Conditional routing ve decision making

### ✅ **Multi-Agent Sistemler:**
- Researcher, Analyst, Writer agent'ları
- Agent koordinasyonu ve iş bölümü
- Quality control ve feedback loops

### ✅ **Gelişmiş Patterns:**
- Human-in-the-loop workflows
- Error handling ve recovery
- Persistent state management

### ✅ **Gerçek Proje:**
- E-ticaret müşteri hizmetleri sistemi
- Sentiment analysis ve urgency detection
- Escalation logic ve response generation

### 🔜 **Sonraki Bölümde:**
- Tam entegrasyon örnekleri
- Performance optimization
- Production deployment
- Monitoring ve analytics

Bu bölümle LangGraph'ın gücünü ve karmaşık workflow'ları nasıl tasarlayacağınızı öğrendiniz. Son bölümde tüm teknolojileri bir araya getireceğiz!