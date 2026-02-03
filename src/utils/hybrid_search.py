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


# Frases de boilerplate legal para penalización
BLACKLIST_PHRASES = [
    "La Administración ostenta las siguientes prerrogativas",
    "Interpretación del contrato",
    "Resolución de las dudas que ofrezca su cumplimiento",
    "Modificación del contrato por razones de interés público",
    "Acordar la resolución del contrato y determinar sus efectos",
    "Establecer penalidades por incumplimiento",
    "cláusulas administrativas particulares",
    "Pliego de Clausulas Administrativas Particulares",
    "El presente contrato tiene carácter administrativo especial",
    "El orden jurisdiccional contencioso-administrativo será el competente"
]

# Patrones de normativas técnicas críticas (Fix INF_05)
LEGISLATIVE_PATTERNS = [
    r'STANAG\s+\d{4}',
    r'ISO\s+\d+',
    r'MIL-STD-\d+',
    r'PECAL\s+\d+',
    r'AQAP\s+\d+',
    r'DEF-STAN'
]

def calculate_final_score(doc: Dict, query: str) -> float:
    """Calcula score final aplicando penalizaciones y boosts."""
    content = doc.get("contenido", "")
    meta = doc.get("metadata", {})
    score = doc.get("metadata", {}).get("rrf_score", 0.0)
    
    # 1. PENALIZACIÓN POR BOILERPLATE
    penalty_multiplier = 1.0
    for phrase in BLACKLIST_PHRASES:
        if phrase in content:
            # Contar ocurrencias o densidad podría ser mejor, pero por ahora presencia fuerte
            if len(content) < 1000: # Si es corto y tiene boilerplate, es casi puro boilerplate
                penalty_multiplier = 0.1
                break
            elif content.count(phrase) > 0:
                 penalty_multiplier *= 0.5 # Penalización acumulativa suave si es largo
    
    score *= penalty_multiplier
    
    # IMPORTANTE: Importar re aquí si no está arriba, o usar el del módulo
    import re

    # 2. BOOSTING DE METADATOS
    # Campos a verificar: num_contrato, empresa, titulo (si existe), archivo
    boost = 0.0
    query_lower = query.lower()
    
    # Extraer keywords clave de la query (limpiando puntuación)
    # Solo letras y números, minúsculas
    clean_query = re.sub(r'[^\w\s]', '', query_lower)
    keywords = [k for k in clean_query.split() if len(k) > 3]
    
    # Verificar coincidencias en metadata
    meta_values = [
        str(meta.get("num_contrato", "")).lower(),
        str(meta.get("empresa", "")).lower(),
        str(meta.get("archivo", "")).lower()
    ]
    
    for kw in keywords:
        # Boost por Metadata (Documento correcto)
        for val in meta_values:
            if kw in val:
                boost += 1.0
                logger.info(f"🚀 Metadata Boost: '{kw}' encontrado en '{val}' (+1.0)")
        
        # Boost por Contenido (Chunk correcto dentro del documento)
        # Si la keyword (ej: "aval") aparece en el texto, sube este chunk
        if kw in content.lower():
            boost += 0.2
            # logger.info(f"  -> Content Boost: '{kw}' en contenido (+0.2)")

    # 3. BOOSTING LEGISLATIVO (Fix INF_05)
    # Si la query pregunta por normativas, priorizar chunks que citan estándares
    # Detectar intención legislativa
    legislative_keywords = ["normativa", "estándar", "standard", "regulación", "stanag", "iso", "mil-std", "pecal", "aqap"]
    is_legislative_query = any(k in query_lower for k in legislative_keywords)
    
    if is_legislative_query:
        for pattern in LEGISLATIVE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                # Boost significativo para asegurar que sobreviva al re-ranking
                boost += 1.5
                logger.info(f"📜 Legislative Boost: Patrón '{pattern}' encontrado en chunk (+1.5)")
                break # Basta con un match para boostear

    return score + boost

def hybrid_search(query: str, top_k: int = 5, vector_weight: float = 0.7, filter_metadata: Dict = None) -> List[Dict]:
    """
    Búsqueda híbrida: combina BM25 (léxico) + Vector (semántico).
    
    Args:
        query: Query del usuario
        top_k: Número de resultados finales
        vector_weight: Peso del vector search (0-1), BM25 = 1 - vector_weight
        filter_metadata: Filtro opcional para metadata (ej: {"num_contrato": "CON_2024_012"})
    
    Returns:
        Lista de chunks rankeados con RRF + boosts
    """
    import time
    start = time.time()
    logger.info(f"Hybrid search para: '{query[:60]}...'")
    
    # PASO 1: Vector Search (ChromaDB)
    print(f"  → Vector search (top 50)...")
    vector_results = vector_search(query, k=50, where=filter_metadata)
    vector_time = time.time() - start
    print(f"    Vector search DONE in {vector_time:.2f}s")
    
    # PASO 2: BM25 Search (Lexical)
    start_bm25 = time.time()
    print(f"  → BM25 search (top 50)...")
    bm25_index = get_bm25_index()
    bm25_results = bm25_index.search(query, top_k=50)
    
    # Aplicar filtro de metadata a resultados BM25 si se especifica
    if filter_metadata:
        filtered_bm25 = []
        for result in bm25_results:
            meta = result.get("metadata", {})
            # Verificar que todos los filtros coincidan
            if all(meta.get(k) == v for k, v in filter_metadata.items()):
                filtered_bm25.append(result)
        bm25_results = filtered_bm25
    
    bm25_time = time.time() - start_bm25
    print(f"    BM25 search DONE in {bm25_time:.2f}s")
    
    # PASO 3: Fusión con RRF
    start_rrf = time.time()
    print(f"  → Fusionando con RRF...")
    fused_results = reciprocal_rank_fusion([vector_results, bm25_results])
    rrf_time = time.time() - start_rrf
    print(f"    RRF fusion DONE in {rrf_time:.2f}s")
    
    # PASO 4: Metadata Boosting & Anti-Boilerplate
    start_boost = time.time()
    print(f"  → Aplicando Metadata Boosting & Anti-Boilerplate...")
    for doc in fused_results:
        doc['metadata']['final_score'] = calculate_final_score(doc, query)
    
    # Re-ordenar por final_score
    fused_results.sort(key=lambda x: x['metadata']['final_score'], reverse=True)
    
    # Top K final
    final_results = fused_results[:top_k]
    
    total_time = time.time() - start
    print(f"  ✅ Hybrid search completado: {len(final_results)} resultados. Total time: {total_time:.2f}s")
    
    return final_results
