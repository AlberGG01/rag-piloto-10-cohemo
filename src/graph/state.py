# -*- coding: utf-8 -*-
"""
Workflow State - Estado compartido entre todos los agents del grafo.
"""

from typing import TypedDict, List, Dict, Optional, Annotated, Literal
from operator import add


class SubQuery(TypedDict):
    """Estructura de una sub-consulta planificada."""
    id: int
    query: str
    rationale: str
    dependency: Optional[List[int]]


class EvaluationReport(TypedDict):
    """Reporte formal de evaluación de suficiencia."""
    status: Literal["SUFFICIENT", "PARTIAL", "INSUFFICIENT"]
    reasoning: str
    missing_info: List[str]
    score: float


class WorkflowState(TypedDict):
    """
    Estado global del workflow agentic RAG.
    """
    
    # Input
    query: str 
    chat_history: List[Dict]
    
    # Planning
    query_complexity: str
    sub_queries: List[SubQuery]
    execution_plan: str
    
    # Retrieval
    retrieved_chunks: Annotated[List[Dict], add]
    retrieval_metadata: Dict
    
    # Evaluation
    evaluation_report: Optional[EvaluationReport]
    evaluation_score: float
    is_sufficient: bool
    
    # Corrective
    corrective_iteration: int           # Default 0, incrementa en cada loop
    refined_queries: List[str]          # Historial de queries refinadas
    retry_count: int                    # Nuevo campo explícito solicitado
    
    # Synthesis
    final_answer: str
    sources: List[Dict]
    confidence: float
    
    # Control flow
    next_agent: str
    error: Optional[str]
