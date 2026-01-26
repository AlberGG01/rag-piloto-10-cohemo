# -*- coding: utf-8 -*-
"""
Búsqueda híbrida: BM25 + Vector Search con Reciprocal Rank Fusion.
"""

import logging
from typing import List, Dict
from src.utils.vectorstore import search as vector_search
from src.utils.bm25_index import BM25Index

logger = logging.getLogger(__name__)

# Instancia global del índice BM25
_bm25_index = None


def get_bm25_index() -> BM25Index:
    """Obtiene el índice BM25 (lazy load con caché)."""
    global _bm25_index
    
    if _bm25_index is None:
        _bm25_index = BM25Index()
        _bm25_index.load()
        logger.info("Índice BM25 cargado en memoria")
    
    return _bm25_index


def reciprocal_rank_fusion(results_list: List[List[Dict]], k: int = 60) -> List[Dict]:
    """
    Fusiona múltiples rankings usando Reciprocal Rank Fusion (RRF).
    
    Args:
        results_list: Lista de listas de resultados (cada una es un ranking)
        k: Constante RRF (default 60, estándar en literatura)
    
    Returns:
        Lista fusionada y re-rankeada
    """
    # Mapear documentos por ID único
    doc_scores = {}
    
    for results in results_list:
        for rank, doc in enumerate(results, 1):
            # Crear ID único del documento (primeros 100 chars del contenido)
            doc_id = doc['contenido'][:100]
            
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    'doc': doc,
                    'rrf_score': 0.0,
                    'ranks': []
                }
            
            # Calcular RRF score: 1 / (k + rank)
            doc_scores[doc_id]['rrf_score'] += 1.0 / (k + rank)
            doc_scores[doc_id]['ranks'].append(rank)
    
    # Ordenar por RRF score descendente
    fused = sorted(
        doc_scores.values(),
        key=lambda x: x['rrf_score'],
        reverse=True
    )
    
    # Retornar solo los documentos con metadata de RRF
    results = []
    for item in fused:
        doc = item['doc'].copy()
        doc['metadata']['rrf_score'] = item['rrf_score']
        doc['metadata']['rrf_ranks'] = item['ranks']
        results.append(doc)
    
    return results


def hybrid_search(query: str, top_k: int = 5, vector_weight: float = 0.7) -> List[Dict]:
    """
    Búsqueda híbrida: combina BM25 (léxico) + Vector (semántico).
    
    Args:
        query: Query del usuario
        top_k: Número de resultados finales
        vector_weight: Peso del vector search (0-1), BM25 = 1 - vector_weight
    
    Returns:
        Top-K chunks fusionados con RRF
    """
    logger.info(f"Hybrid search para: '{query[:50]}...'")
    
    # 1. Búsqueda vectorial (semántica)
    logger.info("  → Vector search (top 20)...")
    vector_results = vector_search(query, k=20)
    
    # 2. Búsqueda BM25 (léxica)
    logger.info("  → BM25 search (top 20)...")
    bm25_index = get_bm25_index()
    bm25_results = bm25_index.search(query, top_k=20)
    
    # 3. Fusionar con RRF
    logger.info("  → Fusionando con RRF...")
    fused_results = reciprocal_rank_fusion([
        vector_results,
        bm25_results
    ])
    
    # 4. Top-K final
    final_results = fused_results[:top_k]
    
    logger.info(f"  ✅ Hybrid search completado: {len(final_results)} resultados")
    
    return final_results
