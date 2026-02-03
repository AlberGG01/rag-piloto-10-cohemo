# -*- coding: utf-8 -*-
"""
Script de depuración profunda de Retrieval.
Verifica si los documentos objetivo aparecen en Vector Search o BM25 individualmente.
"""
import sys
import logging
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.vectorstore import search as vector_search
from src.utils.bm25_index import BM25Index

# Configurar logging detallado
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def debug_query(query: str, target_filename_part: str):
    print("\n" + "="*80)
    print(f"🐛 DEBUG QUERY: '{query}'")
    print(f"🎯 TARGET: Archivo que contenga '{target_filename_part}'")
    print("="*80)
    
    # 1. Test Vector Search
    print("\n🔍 1. VECTOR SEARCH (Top 20)")
    v_results = vector_search(query, k=20)
    found_v = False
    for i, res in enumerate(v_results, 1):
        fname = res['metadata'].get('archivo', 'N/A')
        print(f"   [{i}] {fname} (Dist: {res['distancia']:.4f})")
        if target_filename_part.lower() in fname.lower():
            print(f"      ✅ MATCH FOUND en posición {i}!")
            found_v = True
            
    if not found_v:
        print("   ❌ TARGET NO ENCONTRADO en Vector Top 20.")
        
    # 2. Test BM25
    print("\n📚 2. BM25 SEARCH (Top 20)")
    bm25 = BM25Index()
    bm25.load()
    b_results = bm25.search(query, top_k=20)
    found_b = False
    for i, res in enumerate(b_results, 1):
        fname = res['metadata'].get('archivo', 'N/A')
        print(f"   [{i}] {fname} (Score: {res['score']:.4f})")
        if target_filename_part.lower() in fname.lower():
            print(f"      ✅ MATCH FOUND en posición {i}!")
            found_b = True
            
    if not found_b:
        print("   ❌ TARGET NO ENCONTRADO en BM25 Top 20.")

def main():
    # Caso Retamares
    debug_query("¿Cuál es el importe exacto del contrato de Retamares?", "Retamares")
    
    # Caso IVECO
    debug_query("¿Cuál es el código de aval del contrato con IVECO?", "IVECO")

if __name__ == "__main__":
    main()
