# -*- coding: utf-8 -*-
"""
Hierarchical Retrieval - Escalable a 200+ documentos
"""

import logging
from typing import List, Dict
from collections import defaultdict

from src.utils.hybrid_search import hybrid_search

logger = logging.getLogger(__name__)


def hierarchical_retrieval(query: str, 
                          top_docs: int = 15, 
                          chunks_per_doc: int = 3,
                          initial_k: int = 50) -> List[Dict]:
    """
    Retrieval jerárquico con garantía de diversidad de documentos.
    
    STAGE 1: Hybrid search → 50 chunks iniciales
    STAGE 2: Agrupar por documento
    STAGE 3: Rankear documentos por mejor chunk
    STAGE 4: Seleccionar top-N chunks por documento
    
    Args:
        query: Query del usuario
        top_docs: Documentos únicos a recuperar (default 15)
        chunks_per_doc: Chunks por documento (default 3)
        initial_k: Chunks iniciales a recuperar (default 50)
    
    Returns:
        List[Dict]: top_docs × chunks_per_doc chunks finales
        
    Example:
        # Para 20 docs: 15 docs × 3 chunks = 45 chunks
        # Para 200 docs: 30 docs × 2 chunks = 60 chunks
    """
    
    logger.info(f"Hierarchical retrieval: query='{query[:50]}...', top_docs={top_docs}, chunks_per_doc={chunks_per_doc}")
    
    # STAGE 1: Hybrid search inicial (amplia surface area)
    initial_chunks = hybrid_search(query, top_k=initial_k)
    
    if not initial_chunks:
        logger.warning("No se encontraron chunks en hybrid search")
        return []
    
    # STAGE 2: Agrupar por documento
    docs_dict = defaultdict(list)
    
    for chunk in initial_chunks:
        # Extraer doc_id del archivo
        archivo = chunk['metadata'].get('archivo', '')
        if archivo:
            # "CON_2024_001_..." -> "CON_2024_001"
            doc_id = '_'.join(archivo.split('_')[:3]) if '_' in archivo else archivo
            docs_dict[doc_id].append(chunk)
    
    if not docs_dict:
        logger.warning("No se pudieron agrupar chunks por documento")
        return initial_chunks[:top_docs * chunks_per_doc]
    
    logger.info(f"Agrupados en {len(docs_dict)} documentos únicos")
    
    # STAGE 3: Rankear documentos por mejor chunk score
    doc_scores = {}
    
    for doc_id, chunks in docs_dict.items():
        # Score del documento = promedio de top 3 chunks
        chunk_scores = [c['metadata'].get('rrf_score', 0) for c in chunks]
        top_scores = sorted(chunk_scores, reverse=True)[:min(3, len(chunk_scores))]
        doc_scores[doc_id] = sum(top_scores) / len(top_scores) if top_scores else 0
    
    # Top N documentos
    top_doc_ids = sorted(
        doc_scores.keys(), 
        key=lambda x: doc_scores[x], 
        reverse=True
    )[:top_docs]
    
    logger.info(f"Top {len(top_doc_ids)} documentos seleccionados")
    
    # STAGE 4: Seleccionar mejores chunks por documento
    final_chunks = []
    
    for doc_id in top_doc_ids:
        doc_chunks = docs_dict[doc_id]
        
        # Ordenar chunks del documento por score
        doc_chunks_sorted = sorted(
            doc_chunks,
            key=lambda x: x['metadata'].get('rrf_score', 0),
            reverse=True
        )
        
        # Tomar top N chunks del documento
        selected = doc_chunks_sorted[:chunks_per_doc]
        final_chunks.extend(selected)
    
    logger.info(f"Hierarchical retrieval completado: {len(final_chunks)} chunks de {len(top_doc_ids)} docs únicos")
    
    return final_chunks
