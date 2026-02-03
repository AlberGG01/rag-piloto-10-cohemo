# -*- coding: utf-8 -*-
"""
Script de auditoría de Fase 1: Recuperación de Datos (Retrieval).
Realiza búsqueda híbrida (ChromaDB + BM25) sin generación, para validar retrieval.
"""
import sys
import logging
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.hybrid_search import hybrid_search

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def audit_query(query: str, target_snippet: str, target_alternatives: list = None):
    print("\n" + "="*80)
    print(f"🔍 AUDITORÍA RETRIEVAL: '{query}'")
    print("="*80)
    
    # Ejecutar Hybrid Search
    chunks = hybrid_search(query, top_k=3)
    
    found = False
    
    print(f"\n📊 TOP 3 CHUNKS RECUPERADOS:\n")
    
    for i, chunk in enumerate(chunks, 1):
        content = chunk.get("contenido", "")
        meta = chunk.get("metadata", {})
        rrf_score = meta.get("rrf_score", 0.0)
        distancia = chunk.get("distancia", "N/A") # De vector search
        bm25_score = chunk.get("score", "N/A")    # De BM25 (si disponible)
        
        # Identificar fuente de scores
        scores_str = f"RRF: {rrf_score:.4f}"
        if distancia != "N/A":
            scores_str += f" | Vector Dist: {distancia}"
        if bm25_score != "N/A":
            scores_str += f" | BM25 Score: {bm25_score}"
            
        print(f"🔹 [RANK {i}] {meta.get('archivo', 'Unknown')} ({scores_str})")
        print(f"   Contexto: {content[:300]}...") # Primeros 300 chars
        print("-" * 60)
        
        # Verificar Target
        has_target = target_snippet in content
        if not has_target and target_alternatives:
            for alt in target_alternatives:
                if alt in content:
                    has_target = True
                    print(f"   ✅ MATCH IDENTIFICADOR (Alternativo): '{alt}' encontrado.")
                    break
        
        if has_target:
            print(f"   ✅ MATCH IDENTIFICADOR: '{target_snippet}' encontrado.")
            found = True
    
    if found:
        print("\n✅ RESULTADO: Pasa auditoría de Retrieval.")
    else:
        print(f"\n❌ RESULTADO: FALLO DE RETRIEVAL. '{target_snippet}' no encontrado en Top 3.")

def main():
    print("🚀 INICIANDO AUDITORÍA FASE 1: RETRIEVAL\n")
    
    # 1. Caso Retamares
    audit_query(
        "¿Cuál es el importe exacto del contrato de Retamares?",
        "28.500.000,00",
        target_alternatives=["28.500.000", "28,5M", "28.5M"]
    )
    
    # 2. Caso IVECO
    audit_query(
        "¿Cuál es el código de aval del contrato con IVECO?",
        "AV-2024-1717",
        target_alternatives=["AV 2024 1717"]
    )

if __name__ == "__main__":
    main()
