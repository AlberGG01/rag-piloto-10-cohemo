# -*- coding: utf-8 -*-
"""
ANÁLISIS FORENSE: EDGE_01
Lista los contratos que citan la norma ISO 9001 de forma genérica (sin certificación específica)
Expected: CON_2024_018, SUM_2024_011
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.hybrid_search import hybrid_search
from src.utils.reranker import rerank_chunks
from src.agents.rag_agent import route_query, chat

QUERY = "Lista los contratos que citan la norma ISO 9001 de forma genérica (sin certificación específica)"
EXPECTED = ["CON_2024_018", "SUM_2024_011"]

print("="*80)
print("🔬 ANÁLISIS FORENSE: EDGE_01")
print("="*80)
print(f"\n📝 Query: {QUERY}")
print(f"✅ Expected: {', '.join(EXPECTED)}\n")

# PASO 1: Hybrid search
print("\n" + "="*80)
print("PASO 1: HYBRID SEARCH (top 30)")
print("="*80)
chunks_raw = hybrid_search(QUERY, top_k=30, filter_metadata=None)
print(f"\n📊 Total chunks: {len(chunks_raw)}")

# Buscar los contratos esperados
print("\n🎯 BÚSQUEDA DE CONTRATOS ESPERADOS:")
for expected_contract in EXPECTED:
    found = False
    for i, chunk in enumerate(chunks_raw, 1):
        if expected_contract in chunk.get('metadata', {}).get('source', ''):
            found = True
            print(f"\n✅ {expected_contract} en posición #{i}")
            content = chunk.get('contenido', '')
            if 'ISO 9001' in content or 'ISO9001' in content:
                print(f"   Contiene 'ISO 9001': ✅")
                print(f"   Snippet: {content[:200]}...")
            else:
                print(f"   Contiene 'ISO 9001': ❌")
    
    if not found:
        print(f"\n❌ {expected_contract} NO encontrado en top-30")

# Ver qué fuentes SÍ recuperó
print("\n📂 FUENTES EN TOP-10:")
for i, chunk in enumerate(chunks_raw[:10], 1):
    source = chunk.get('metadata', {}).get('source', 'unknown')
    content = chunk.get('contenido', '')[:100]
    print(f"{i}. {source}")
    print(f"   {content}...")

# PASO 2: Re-ranking
print("\n" + "="*80)
print("PASO 2: RE-RANKING (top 10)")
print("="*80)
chunks_reranked = rerank_chunks(QUERY, chunks_raw, top_k=10)

print("\n🎯 ¿CONTRATOS ESPERADOS SOBREVIVIERON?")
for expected_contract in EXPECTED:
    found = False
    for i, chunk in enumerate(chunks_reranked, 1):
        if expected_contract in chunk.get('metadata', {}).get('source', ''):
            found = True
            print(f"✅ {expected_contract} en posición #{i} post-rerank")
    
    if not found:
        print(f"❌ {expected_contract} ELIMINADO por re-ranking")

# PASO 3: Respuesta RAG
print("\n" + "="*80)
print("PASO 3: RESPUESTA RAG")
print("="*80)
response = chat(QUERY, [])
print(f"\n📄 Respuesta (primeros 500 chars):\n{response[:500]}...\n")

# CONCLUSIÓN
print("\n" + "="*80)
print("🎯 DIAGNÓSTICO")
print("="*80)

found_in_response = [c for c in EXPECTED if c in response]
print(f"\nContratos esperados ({len(EXPECTED)}): {', '.join(EXPECTED)}")
print(f"Contratos en respuesta ({len(found_in_response)}): {', '.join(found_in_response) if found_in_response else 'NINGUNO'}")

if len(found_in_response) == len(EXPECTED):
    print("\n✅ RESPUESTA CORRECTA")
elif len(found_in_response) == 0:
    print("\n❌ RESPUESTA COMPLETAMENTE INCORRECTA")
else:
    print(f"\n⚠️ RESPUESTA PARCIAL ({len(found_in_response)}/{len(EXPECTED)})")
