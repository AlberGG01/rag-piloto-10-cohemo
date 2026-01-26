# -*- coding: utf-8 -*-
"""
Re-ranking de chunks usando GPT-4o para mejorar precisión.
"""

import logging
import json
import re
from typing import List, Dict
from src.utils.llm_config import generate_response

logger = logging.getLogger(__name__)


def rerank_with_llm(query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
    """
    Re-rankea chunks candidatos usando GPT-4o.
    
    Args:
        query: Query original del usuario
        candidates: Lista de chunks candidatos (del hybrid search)
        top_k: Cuántos chunks retornar
    
    Returns:
        Top-K chunks re-rankeados por relevancia
    """
    if len(candidates) <= top_k:
        return candidates
    
    # Limitar a 10 candidatos para no saturar el prompt
    candidates_to_rank = candidates[:10]
    
    # Crear texto de candidatos
    candidates_text = ""
    for i, chunk in enumerate(candidates_to_rank, 1):
        snippet = chunk['contenido'][:400]  # Primeros 400 chars
        candidates_text += f"\n\n[Doc {i}]\n{snippet}..."
    
    # Prompt de re-ranking
    prompt = f"""Eres un experto en evaluar relevancia de documentos.

QUERY DEL USUARIO: "{query}"

DOCUMENTOS CANDIDATOS:
{candidates_text}

TAREA:
Evalúa qué documentos son MÁS relevantes para responder la query.
Asigna un score de 0-10 a cada documento según su relevancia.

IMPORTANTE:
- 10 = Responde directamente la pregunta
- 7-9 = Información muy relacionada
- 4-6 = Información parcialmente relacionada  
- 0-3 = Poco o nada relevante

Responde SOLO con JSON en este formato:
[{{"doc_id": 1, "score": 9}}, {{"doc_id": 2, "score": 7}}, ...]

Ordena de mayor a menor score."""

    try:
        # Generar scores
        response = generate_response(prompt, max_tokens=300, temperature=0.0)
        
        # Parsear JSON
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group())
            
            # Reordenar según scores
            reranked = []
            for item in scores:
                doc_id = item.get('doc_id', 0)
                score = item.get('score', 0)
                
                # Validar índice
                if 1 <= doc_id <= len(candidates_to_rank):
                    chunk = candidates_to_rank[doc_id - 1].copy()
                    chunk['metadata']['rerank_score'] = score
                    reranked.append(chunk)
            
            # Retornar top-K
            if reranked:
                logger.info(f"Re-ranking: {len(reranked)} chunks ordenados por relevancia")
                return reranked[:top_k]
        
    except Exception as e:
        logger.warning(f"Error en re-ranking LLM: {e}. Usando orden original.")
    
    # Fallback: retornar orden original
    return candidates[:top_k]
