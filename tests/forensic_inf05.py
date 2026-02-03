# -*- coding: utf-8 -*-
"""
ANÁLISIS FORENSE: INF_05
¿Qué normativa de seguridad alimentaria aplica al suministro de raciones de combate individual?
Expected: STANAG 2937 (NATO)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.hybrid_search import hybrid_search
from src.utils.reranker import rerank_chunks
from src.agents.rag_agent import chat

QUERY = "¿Qué normativa de seguridad alimentaria aplica al suministro de raciones de combate individual?"
EXPECTED_TEXT = "STANAG 2937"

print("="*80)
print("🔬 ANÁLISIS FORENSE: INF_05")
print("="*80)
print(f"\n📝 Query: {QUERY}")
print(f"✅ Expected: {EXPECTED_TEXT}\n")

# Hybrid search
print("\n" + "="*80)
print("PASO 1: HYBRID SEARCH")
print("="*80)
chunks_raw = hybrid_search(QUERY, top_k=15, filter_metadata=None)

# Buscar STANAG 2937
found_stanag = False
print("\n🎯 BÚSQUEDA DE 'STANAG 2937':")
for i, chunk in enumerate(chunks_raw, 1):
    content = chunk.get('contenido', '')
    if 'STANAG' in content.upper():
        found_stanag = True
        source = chunk.get('metadata', {}).get('source', 'unknown')
        print(f"\n✅ 'STANAG' encontrado en posición #{i}")
        print(f"   Source: {source}")
        print(f"   Contenido: {content[:300]}...")

if not found_stanag:
    print(f"\n❌ 'STANAG 2937' NO encontrado en chunks")
    print("\n🔍 Buscando 'raciones' o 'combate':")
    for i, chunk in enumerate(chunks_raw[:5], 1):
        content = chunk.get('contenido', '')
        source = chunk.get('metadata', {}).get('source', '')
        if 'racion' in content.lower() or 'combate' in content.lower():
            print(f"\n{i}. {source}")
            print(f"   {content[:200]}...")

# Respuesta RAG
print("\n" + "="*80)
print("PASO 2: RESPUESTA RAG")
print("="*80)
response = chat(QUERY, [])
print(f"\n📄 {response[:600]}...\n")

# Diagnóstico
if EXPECTED_TEXT in response:
    print(f"✅ Respuesta contiene '{EXPECTED_TEXT}'")
else:
    print(f"❌ Respuesta NO contiene '{EXPECTED_TEXT}'")
    print(f"\n🔍 ¿Qué normativa menciona la respuesta?")
    if 'ISO' in response:
        print("   → Menciona ISO (INCORRECTO)")
    if 'STANAG' in response:
        print(f"   → Menciona STANAG (revisar si es correcto)")
