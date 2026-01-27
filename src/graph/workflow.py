# -*- coding: utf-8 -*-
"""
Agentic RAG Workflow - Orquestación con LangGraph
"""


import logging
from typing import Literal, Dict

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from src.graph.state import WorkflowState
from src.agents.context_rewriter import ContextRewriter
from src.agents.orchestrator import OrchestratorAgent

logger = logging.getLogger(__name__)


def create_workflow() -> StateGraph:
    """
    Crea el grafo de workflow para el sistema agentic RAG.
    
    Returns:
        StateGraph: Grafo configurado listo para compilar
    """
    
    # Crear grafo
    workflow = StateGraph(WorkflowState)
    
    # Inicializar agents
    from src.agents.orchestrator import OrchestratorAgent
    from src.agents.planner import PlanningAgent
    from src.agents.retrieval import RetrievalAgent
    from src.agents.evaluator import EvaluationAgent
    from src.agents.corrective import CorrectiveAgent
    from src.agents.synthesis import SynthesisAgent
    
    rewriter = ContextRewriter()
    orchestrator = OrchestratorAgent()
    planner = PlanningAgent()
    retrieval = RetrievalAgent()
    evaluator = EvaluationAgent()
    corrective = CorrectiveAgent()
    synthesis = SynthesisAgent()
    
    # Agregar nodos al grafo
    workflow.add_node("rewriter", rewriter.rewrite)
    workflow.add_node("orchestrator", orchestrator.run)
    workflow.add_node("planner", planner.run)
    workflow.add_node("retrieval", retrieval.run)
    workflow.add_node("evaluator", evaluator.run)
    workflow.add_node("corrective", corrective.run)
    workflow.add_node("synthesis", synthesis.run)
    
    # Definir punto de entrada (Ahora es el Rewriter)
    workflow.set_entry_point("rewriter")
    
    # Definir edges normales
    workflow.add_edge("rewriter", "orchestrator")
    workflow.add_edge("orchestrator", "planner")
    workflow.add_edge("planner", "retrieval")
    workflow.add_edge("retrieval", "evaluator")
    workflow.add_edge("corrective", "retrieval")
    workflow.add_edge("synthesis", END) # Final del flujo
    
    # Definir conditional edges para el evaluador
    def route_after_evaluation(state: WorkflowState):
        """Decide a dónde ir después de evaluar."""
        report = state.get("evaluation_report", {})
        status = report.get("status", "INSUFFICIENT")
        
        # Recuperar contador de retry
        retry_count = state.get("retry_count", 0)
        MAX_RETRIES = 2
        
        if status == "SUFFICIENT":
            return "synthesis"  # -> Synthesis directo
        else:
            if retry_count >= MAX_RETRIES:
                # Límite alcanzado, sintetizar lo que haya
                return "synthesis"
            
            # Si falta info y tenemos intentos, corregir
            return "corrective"

    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "synthesis": "synthesis",
            "corrective": "corrective"
        }
    )
    
    logger.info("✅ Workflow graph creado con éxito (v3.0 Contextual)")
    
    return workflow



# Singleton MemorySaver para persistencia en memoria durante la vida del proceso
_shared_memory = MemorySaver()

def compile_workflow(checkpointer=None) -> any:
    """
    Compila el workflow en un ejecutable.
    
    Args:
        checkpointer: Objeto de persistencia (MemorySaver, etc)
        
    Returns:
        Compiled graph listo para ejecutar
    """
    workflow = create_workflow()
    compiled = workflow.compile(checkpointer=checkpointer)
    
    logger.info(f"✅ Workflow compilado (Checkpointer: {checkpointer is not None})")
    
    return compiled


# Función helper para invocar el workflow
def run_agentic_rag(query: str, chat_history: list = None, thread_id: str = None) -> Dict:
    """
    Ejecuta el workflow agentic RAG end-to-end.
    
    Args:
        query: Query del usuario
        chat_history: Historial de chat (opcional)
        thread_id: ID de sesión para memoria persistente (opcional)
    
    Returns:
        Dict con resultado final
    """
    
    # Configurar memoria si hay thread_id
    # USAMOS LA MEMORIA COMPARTIDA PARA QUE PERSISTA ENTRE LLAMADAS
    checkpointer = _shared_memory if thread_id else None
    
    # Inicializar inputs para el grafo
    inputs = {
        "query": query,
        # Reset transient fields
        "retry_count": 0,
        "corrective_iteration": 0,
        "is_sufficient": False,
        "evaluation_report": None,
        "final_answer": "",
        "error": None
    }
    
    # Solo inyectar chat_history si se proporciona explícitamente o si NO hay thread_id (stateless)
    # Si hay thread_id y chat_history es None/Empty, dejamos que el grafo use su memoria.
    if chat_history is not None or not thread_id:
        inputs["chat_history"] = chat_history or []

    # Compilar y ejecutar
    app = compile_workflow(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": thread_id}} if thread_id else None
    
    try:
        # Usamos 'inputs' en lugar de 'initial_state' completo, LangGraph fusionará.
        result = app.invoke(inputs, config=config)
        
        return {
            "answer": result.get("final_answer", ""),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
            "metadata": {
                "rewritten_query": result.get("query", ""), # La query final en el estado es la reescrita
                "complexity": result.get("query_complexity", ""),
                "iterations": result.get("corrective_iteration", 0),
                "retry_count": result.get("retry_count", 0),
                "evaluation_score": result.get("evaluation_score", 0.0),
                "execution_plan": result.get("execution_plan", ""),
                "sub_queries": result.get("sub_queries", []),
                "retrieval_report": result.get("retrieval_metadata", {}),
                "evaluation_report": result.get("evaluation_report", {})
            }
        }
    
    except Exception as e:
        logger.error(f"Error en workflow: {e}")
        return {
            "answer": f"Error procesando la consulta: {str(e)}",
            "sources": [],
            "confidence": 0.0,
            "metadata": {"error": str(e)}
        }
