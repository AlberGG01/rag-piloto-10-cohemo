# -*- coding: utf-8 -*-
"""
Configuración LLM - OpenAI only.
"""

import logging
from pathlib import Path
from typing import Optional

from openai import OpenAI

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import OPENAI_API_KEY, MODEL_CHATBOT

logger = logging.getLogger(__name__)

# Cliente OpenAI global (cache)
_openai_client: Optional[OpenAI] = None


def _get_openai_client() -> OpenAI:
    """
    Obtiene cliente OpenAI (lazy load con caché).
    
    Returns:
        OpenAI: Cliente configurado
    """
    global _openai_client
    
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Cliente OpenAI inicializado")
    
    return _openai_client


def generate_response(
    prompt: str,
    max_tokens: int = 700,
    temperature: float = 0.0,
    model: str = MODEL_CHATBOT
) -> str:
    """
    Genera respuesta usando OpenAI.
    Allows overriding the model (e.g., use gpt-4o-mini for evaluation).
    
    Args:
        prompt: Prompt completo para el LLM
        max_tokens: Máximo de tokens a generar
        temperature: Temperatura (0.0 = determinista, 1.0 = creativo)
        model: ID del modelo a usar (default: MODEL_CHATBOT)
    
    Returns:
        str: Respuesta generada
    """
    # try-except eliminado para permitir manejo por Tenacity en BaseAgent
    client = _get_openai_client()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content.strip()


def is_model_available() -> bool:
    """
    Verifica si OpenAI está disponible (API Key configurada).
    
    Returns:
        bool: True si API Key está configurada
    """
    return bool(OPENAI_API_KEY and len(OPENAI_API_KEY) > 10)


def get_model_info() -> str:
    """
    Retorna información del modelo configurado.
    
    Returns:
        str: Información del modelo
    """
    if is_model_available():
        return f"OpenAI {MODEL_CHATBOT}"
    else:
        return "Sin modelo configurado (falta OPENAI_API_KEY)"
