# -*- coding: utf-8 -*-
"""
Orchestrator Agent - Punto de entrada y coordinación inicial.
"""

from src.agents.base_agent import BaseAgent
from src.graph.state import WorkflowState


class OrchestratorAgent(BaseAgent):
    """
    Agent orquestador que:
    1. Recibe la query inicial
    2. Inicializa el estado
    3. Decide el flujo inicial (planner o retrieval directo)
    """
    
    def __init__(self):
        super().__init__(name="orchestrator")
    
    def run(self, state: WorkflowState) -> WorkflowState:
        """
        Coordina el inicio del workflow.
        
        Args:
            state: Estado del workflow
        
        Returns:
            WorkflowState actualizado
        """
        
        self.log_start(state)
        
        try:
            query = state["query"]
            
            # Log inicial
            self.logger.info(f"Nueva query recibida: {query[:100]}...")
            
            # Inicializar metadata básica
            state["retrieved_chunks"] = []
            state["sources"] = []
            state["corrective_iteration"] = 0
            
            # Preparar para siguiente paso (planner)
            state["next_agent"] = "planner"
            
            self.logger.info("Orquestación inicial completada, delegando a planner...")
            
            self.log_end(state)
            
        except Exception as e:
            self.log_error(e)
            state["error"] = str(e)
            state["final_answer"] = f"Error en orchestrator: {e}"
        
        return state
