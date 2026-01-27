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
    # PASO 2: Búsqueda vectorial con filtros (si aplica)
    filtered_chunks = []
    if metadata_filters:
        # Búsqueda filtrada
        try:
            filtered_chunks = search(query, k=initial_k, where=metadata_filters)
            logger.info(f"Búsqueda filtrada recuperó {len(filtered_chunks)} chunks")
        except Exception as e:
            logger.warning(f"Error en búsqueda filtrada: {e}")
            filtered_chunks = []

        # FALLBACK: Válvula de Seguridad
        if not filtered_chunks:
            logger.warning("⚠️ FILTRO DEMASIADO ESTRICTO (0 resultados). Aplicando FALLBACK a búsqueda abierta.")
            metadata_filters = None # Desactivar filtros para pasar al bloque else/fallback
    
    if metadata_filters and filtered_chunks:
        # Si tuvimos éxito con filtros, usamos esos chunks
        initial_chunks = filtered_chunks
    else:
        # Búsqueda abierta -> HYBRID SEARCH (BM25 + Vector RRF)
        try:
            from src.utils.hybrid_search import hybrid_search
            # Usamos hybrid_search para capturar tanto semántica como keywords exactas
            # top_k=initial_k (ej. 50) para tener suficiente pool para agrupar por docs
            initial_chunks = hybrid_search(query, top_k=initial_k)
            logger.info(f"Hybrid Search (RRF) recuperó {len(initial_chunks)} chunks")
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}. Falling back to vector only.")
            initial_chunks = search(query, k=initial_k)
            logger.info(f"Búsqueda vectorial (fallback) recuperó {len(initial_chunks)} chunks")
    
    if not initial_chunks:
        logger.warning("No se encontraron chunks")
        return []
    
    # PASO 3: Agrupación por documento
    docs_dict = defaultdict(list)
    
    for chunk in initial_chunks:
        # Intentar varias fuentes para el ID del documento
        meta = chunk.get('metadata', {})
        archivo = meta.get('archivo', '')
        
        # ID Robusto: Archivo base sin _normalized
        if archivo:
            # Normalizar nombre archivo (quitar .pdf, _normalized, etc para agrupar variantes)
            # Ejemplo simplificado
            clean_name = archivo.replace("_normalized.md", "").replace(".pdf", "")
            # Usar expediente si existe podría ser mejor, pero archivo es más seguro como ID único físico
            doc_id = clean_name
        else:
            doc_id = "unknown_doc"
            
        docs_dict[doc_id].append(chunk)
    
    logger.info(f"Agrupados en {len(docs_dict)} documentos únicos")
    
    # PASO 4: DIVERSITY SELECTOR (Round Robin)
    # Seleccionamos chunks iterando por documento para garantizar variedad
    final_chunks = []
    
    # Ordenar chunks dentro de cada documento por relevancia (score de vector/bm25)
    # Asumimos que initial_chunks ya viene ordenado globalmente, pero re-ordenamos localmente por si acaso
    for doc_id in docs_dict:
        # Ordenamos por distancia (menor es mejor) o score (mayor es mejor)
        # BM25 devuelve score, Vector devuelve distancia.
        # Asumimos que el sistema de búsqueda unificado maneja esto, pero aqui
        # solo iteraremos en el orden en que llegaron (que suele ser por score)
        pass 

    # Round Robin
    # Creamos iteradores para cada lista de documentos
    doc_iterators = [iter(chunks) for chunks in docs_dict.values()]
    
    # Límite total de chunks a retornar (para no saturar el contexto ni el reranker)
    # top_docs * chunks_per_doc  aprox, o un fijo
    total_limit = top_docs * chunks_per_doc
    
    active_iterators = doc_iterators[:]
    
    while len(final_chunks) < total_limit and active_iterators:
        full_round_chunks = []
        next_iterators = []
        
        for it in active_iterators:
            try:
                chunk = next(it)
                final_chunks.append(chunk)
                full_round_chunks.append(chunk)
                next_iterators.append(it)
                
                if len(final_chunks) >= total_limit:
                    break
            except StopIteration:
                pass
        
        active_iterators = next_iterators
        if not full_round_chunks:
            break
            
    logger.info(f"Retrieval diverso completado: {len(final_chunks)} chunks seleccionados (Round Robin)")
    
    return final_chunks
