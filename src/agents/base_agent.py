# -*- coding: utf-8 -*-
"""
Base Agent - Clase abstracta para todos los agents del sistema.
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict

from src.graph.state import WorkflowState

from openai import RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
from src.utils.llm_config import generate_response

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Clase base abstracta para todos los agents.
    
    Cada agent debe:
    1. Implementar el método run()
    2. Recibir WorkflowState
    3. Retornar WorkflowState actualizado
    """
    
    def __init__(self, name: str):
        """
        Args:
            name: Nombre identificador del agent
        """
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    def run(self, state: WorkflowState) -> WorkflowState:
        """
        Ejecuta la lógica del agent.
        
        Args:
            state: Estado actual del workflow
        
        Returns:
            WorkflowState: Estado actualizado
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(RateLimitError),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def call_llm(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.0) -> str:
        """
        Llamada segura al LLM con Exponential Backoff para manejar Rate Limits (429).
        Wrappeado con Tenacity:
        - Wait: Exponential (1s a 10s)
        - Stop: 3 intentos
        - Log: Warning antes de dormir
        """
        try:
            return generate_response(prompt, max_tokens, temperature)
        except Exception as e:
            # Re-raise para que Tenacity lo capture si es RateLimitError (o si queremos atrapar todo)
            # generate_response ya no atrapa excepciones, así que 'e' será la excepción raw de OpenAI
            self.logger.warning(f"Intento LLM fallido: {e}")
            raise e

    def log_start(self, state: WorkflowState):
        """Helper para logging de inicio."""
        self.logger.info(f"🤖 {self.name} iniciando...")
        self.logger.debug(f"Query: {state.get('query', 'N/A')[:100]}")
    
    def log_end(self, state: WorkflowState):
        """Helper para logging de fin."""
        self.logger.info(f"✅ {self.name} completado")
    
    def log_error(self, error: Exception):
        """Helper para logging de errores."""
        self.logger.error(f"❌ {self.name} falló: {error}")
