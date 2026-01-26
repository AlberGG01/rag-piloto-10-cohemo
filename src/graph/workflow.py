# -*- coding: utf-8 -*-
"""
Agentic RAG Workflow - Orquestación con LangGraph
"""

import logging
from typing import Literal, Dict

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

from src.graph.state import WorkflowState
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
    
    orchestrator = OrchestratorAgent()
    planner = PlanningAgent()
    retrieval = RetrievalAgent()
    evaluator = EvaluationAgent()
    corrective = CorrectiveAgent()
    synthesis = SynthesisAgent()
    
    # Agregar nodos al grafo
    workflow.add_node("orchestrator", orchestrator.run)
    workflow.add_node("planner", planner.run)
    workflow.add_node("retrieval", retrieval.run)
    workflow.add_node("evaluator", evaluator.run)
    workflow.add_node("corrective", corrective.run)
    workflow.add_node("synthesis", synthesis.run)
    
    # Definir punto de entrada
    workflow.set_entry_point("orchestrator")
    
    # Definir edges normales
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
    
    # TODO: Agregar conditional edges según lógica de routing
    # workflow.add_conditional_edges(
    #     "evaluator",
    #     route_after_evaluation,
    #     {
    #         "sufficient": "synthesis",
    #         "insufficient": "corrective"
    #     }
    # )
    
    logger.info("✅ Workflow graph creado con éxito")
    
    return workflow


def compile_workflow() -> any:
    """
    Compila el workflow en un ejecutable.
    
    Returns:
        Compiled graph listo para ejecutar
    """
    workflow = create_workflow()
    compiled = workflow.compile()
    
    logger.info("✅ Workflow compilado y listo para usar")
    
    return compiled


# Función helper para invocar el workflow
def run_agentic_rag(query: str, chat_history: list = None) -> Dict:
    """
    Ejecuta el workflow agentic RAG end-to-end.
    
    Args:
        query: Query del usuario
        chat_history: Historial de chat (opcional)
    
    Returns:
        Dict con resultado final
    """
    
    # Inicializar estado
    initial_state: WorkflowState = {
        "query": query,
        "chat_history": chat_history or [],
        "query_complexity": "",
        "sub_queries": [],
        "execution_plan": "",
        "retrieved_chunks": [],
        "retrieval_metadata": {},
        "evaluation_score": 0.0,
        "evaluation_critique": "",
        "is_sufficient": False,
        "missing_info": "",
        "corrective_iteration": 0,
        "refined_queries": [],
        "final_answer": "",
        "sources": [],
        "confidence": 0.0,
        "next_agent": "",
        "error": None
    }
    
    # Compilar y ejecutar
    app = compile_workflow()
    
    try:
        result = app.invoke(initial_state)
        
        return {
            "answer": result.get("final_answer", ""),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0.0),
            "metadata": {
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
