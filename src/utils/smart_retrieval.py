# -*- coding: utf-8 -*-
"""
Smart Hierarchical Retrieval - Con filtrado inteligente por metadata
"""

import logging
from typing import List, Dict, Optional
from collections import defaultdict

from src.utils.vectorstore import search
from src.utils.query_analyzer import analyze_query_for_filters

logger = logging.getLogger(__name__)


def smart_hierarchical_retrieval(query: str, 
                                 top_docs: int = 15, 
                                 chunks_per_doc: int = 3,
                                 initial_k: int = 50) -> List[Dict]:
    """
    Retrieval jerárquico CON filtrado inteligente por metadata.
    
    1. Analizar query → detectar filtros de metadata
    2. Búsqueda vectorial con filtros → chunks pre-filtrados
    3. Agrupación por documento
    4. Selección de top_docs documentos
    5. Top chunks_per_doc por documento
    
    Args:
        query: Query del usuario
        top_docs: Documentos únicos a recuperar
        chunks_per_doc: Chunks por documento
        initial_k: Chunks iniciales máximos
    
    Returns:
        Lista de chunks enriquecidos y filtrados
    """
    
    logger.info(f"Smart retrieval: query='{query[:50]}...'")
    
    # PASO 1: Analizar query para filtros inteligentes
    metadata_filters = analyze_query_for_filters(query)
    
    # PASO 2: Búsqueda vectorial con filtros (si aplica)
    if metadata_filters:
        # Búsqueda filtrada
        initial_chunks = search(query, k=initial_k, where=metadata_filters)
        logger.info(f"Búsqueda filtrada recuperó {len(initial_chunks)} chunks")
    else:
        # Búsqueda abierta
        initial_chunks = search(query, k=initial_k)
        logger.info(f"Búsqueda abierta recuperó {len(initial_chunks)} chunks")
    
    if not initial_chunks:
        logger.warning("No se encontraron chunks")
        return []
    
    # PASO 3: Agrupación por documento
    docs_dict = defaultdict(list)
    
    for chunk in initial_chunks:
        archivo = chunk['metadata'].get('archivo', '')
        if archivo:
            doc_id = '_'.join(archivo.split('_')[:3]) if '_' in archivo else archivo
            docs_dict[doc_id].append(chunk)
    
    logger.info(f"Agrupados en {len(docs_dict)} documentos únicos")
    
    # PASO 4: Rankear documentos por mejor chunk
    doc_scores = {}
    for doc_id, chunks in docs_dict.items():
        # Score = promedio de top 3 chunks del documento
        scores = [c.get('distancia', 0) for c in chunks]
        top_scores = sorted(scores)[:min(3, len(scores))]  # Menor distancia = más cercano
        doc_scores[doc_id] = sum(top_scores) / len(top_scores) if top_scores else 999
    
    # Top N documentos (menor score = mejor)
    top_doc_ids = sorted(doc_scores.keys(), key=lambda x: doc_scores[x])[:top_docs]
    
    logger.info(f"Top {len(top_doc_ids)} documentos seleccionados")
    
    # PASO 5: Seleccionar mejores chunks por documento
    final_chunks = []
    
    for doc_id in top_doc_ids:
        doc_chunks = docs_dict[doc_id]
        
        # Ordenar por distancia (menor = mejor)
        doc_chunks_sorted = sorted(doc_chunks, key=lambda x: x.get('distancia', 999))
        
        # Tomar top N
        selected = doc_chunks_sorted[:chunks_per_doc]
        final_chunks.extend(selected)
    
    logger.info(f"Smart retrieval completado: {len(final_chunks)} chunks de {len(top_doc_ids)} docs únicos")
    
    return final_chunks
