# -*- coding: utf-8 -*-
"""
Script para construir el índice BM25 desde la vectorstore existente.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.vectorstore import get_collection
from src.utils.bm25_index import BM25Index

def build_bm25_index():
    """Construye el índice BM25 desde ChromaDB."""
    print("\n" + "=" * 60)
    print("🔍 CONSTRUCCIÓN DE ÍNDICE BM25")
    print("=" * 60)
    
    # 1. Obtener todos los chunks de ChromaDB
    print("\n📊 Obteniendo chunks de ChromaDB...")
    collection = get_collection()
    
    all_data = collection.get()
    
    chunks = []
    for i in range(len(all_data['ids'])):
        chunks.append({
            'contenido': all_data['documents'][i],
            'metadata': all_data['metadatas'][i]
        })
    
    print(f"   ✅ Obtenidos {len(chunks)} chunks")
    
    # 2. Construir índice BM25
    print("\n🔨 Construyendo índice BM25...")
    bm25_index = BM25Index()
    bm25_index.build(chunks)
    
    print("\n" + "=" * 60)
    print("✅ Índice BM25 construido exitosamente")
    print(f"   Documentos indexados: {len(chunks)}")
    print(f"   Ubicación: data/bm25_index.pkl")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    build_bm25_index()
