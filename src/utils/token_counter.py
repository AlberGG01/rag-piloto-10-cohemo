# -*- coding: utf-8 -*-
"""
Token Counter Utility.
Maneja el conteo de tokens y el recorte de contexto para Token Budgeting.
"""

import logging
from typing import List, Dict
import tiktoken

logger = logging.getLogger(__name__)

# Configuración
MODEL_ENCODING = "o200k_base" # Encoding para GPT-4o
MAX_CONTEXT_TOKENS = 20000

def get_encoder():
    """Retorna el encoder de tiktoken para GPT-4o."""
    try:
        return tiktoken.get_encoding(MODEL_ENCODING)
    except Exception as e:
        logger.warning(f"No se pudo cargar encoding {MODEL_ENCODING}, usando cl100k_base. Error: {e}")
        return tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Cuenta los tokens de un texto."""
    encoder = get_encoder()
    return len(encoder.encode(text))

def trim_context(chunks: List[Dict], max_tokens: int = MAX_CONTEXT_TOKENS) -> List[Dict]:
    """
    Recorta la lista de chunks para ajustarse al presupuesto de tokens.
    Prioriza los chunks con mayor 'score' (similitud).
    
    Args:
        chunks: Lista de diccionarios con keys 'contenido', 'metadata', 'score'
        max_tokens: Límite de tokens
        
    Returns:
        List[Dict]: Lista recortada de chunks
    """
    if not chunks:
        return []

    # 1. Ordenar por score descendente (priorizar los más relevantes)
    # Asumimos que si no hay score, es 0.0
    sorted_chunks = sorted(chunks, key=lambda x: x.get("score", 0.0), reverse=True)
    
    selected_chunks = []
    current_tokens = 0
    encoder = get_encoder()
    
    logger.info(f"Iniciando Token Budgeting. Input: {len(chunks)} chunks. Max Tokens: {max_tokens}")
    
    for chunk in sorted_chunks:
        content = chunk.get("contenido", "")
        # Estimamos tokens del chunk (contenido + metadata básica)
        meta_str = str(chunk.get("metadata", {}))
        chunk_text = f"{content}\n{meta_str}"
        
        chunk_tokens = len(encoder.encode(chunk_text))
        
        if current_tokens + chunk_tokens <= max_tokens:
            selected_chunks.append(chunk)
            current_tokens += chunk_tokens
        else:
            logger.debug(f"Chunk descartado por límite de tokens (Size: {chunk_tokens})")
            
    logger.info(f"Token Budgeting completado. Output: {len(selected_chunks)} chunks. Tokens est: {current_tokens}")
    
    # Restaurar orden original o devolver por relevancia?
    # Para síntesis, el orden de relevancia es bueno, pero a veces el orden lógico importa.
    # Dado que es RAG, el orden de relevancia es seguro.
    return selected_chunks
