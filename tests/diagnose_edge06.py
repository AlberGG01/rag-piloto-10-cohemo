# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO FORENSE EDGE_06
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.hybrid_search import hybrid_search
from src.utils.reranker import rerank_chunks
from src.agents.rag_agent import route_query, chat

QUERY = "¿Qué contrato prohíbe explícitamente la subcontratación de actividades 'por razones de seguridad'?"
EXPECTED = "CON_2024_004"

print("="*80)
print("🔍 DIAGNÓSTICO FORENSE: EDGE_06")
print("="*80)
print(f"\n📝 Query: {QUERY}")
print(f"✅ Expected: {EXPECTED}\n")

# PASO 1: Route
print("\n" + "="*80)
print("PASO 1: ROUTE QUERY")
print("="*80)
query_type = route_query(QUERY)
print(f"Query Type: {query_type}")

# PASO 2: Hybrid search
print("\n" + "="*80)
print("PASO 2: HYBRID SEARCH (top 15)")
print("="*80)
chunks_raw = hybrid_search(QUERY, top_k=15, filter_metadata=None)
print(f"\n📊 Total chunks: {len(chunks_raw)}")

# Analizar chunks
print("\n🔝 TOP 5 CHUNKS:")
for i, chunk in enumerate(chunks_raw[:5], 1):
    meta = chunk.get('metadata', {})
    source = meta.get('source', 'unknown')
    page = meta.get('page', '?')
    text = chunk.get('contenido', '')[:100]  # CORREGIDO: 'contenido' no 'page_content'
    print(f"\n{i}. {source} (p{page})")
    print(f"   {text}...")

# Buscar CON_2024_004
print("\n" + "="*80)
print("🎯 ¿ESTÁ CON_2024_004?")
print("="*80)
found_004 = False
for i, chunk in enumerate(chunks_raw, 1):
    if 'CON_2024_004' in chunk.get('metadata', {}).get('source', ''):
        found_004 = True
        print(f"\n✅ CON_2024_004 en posición #{i}")
        print(f"\nCONTENIDO:\n{chunk.get('contenido', '')}\n")  # CORREGIDO

if not found_004:
    print(f"\n❌ CON_2024_004 NO encontrado")
    print("\nSources en top-15:")
    for chunk in chunks_raw:
        print(f"  - {chunk.get('metadata', {}).get('source', 'unknown')}")

# PASO 3: Re-ranking
print("\n" + "="*80)
print("PASO 3: RE-RANKING")
print("="*80)
chunks_reranked = rerank_chunks(QUERY, chunks_raw, top_k=10)
print(f"Chunks reranked: {len(chunks_reranked)}")

# Buscar CON_2024_004 post-rerank
found_004_rerank = False
for i, chunk in enumerate(chunks_reranked, 1):
    if 'CON_2024_004' in chunk.get('metadata', {}).get('source', ''):
        found_004_rerank = True
        print(f"\n✅ CON_2024_004 SOBREVIVIÓ - posición #{i}")

if not found_004_rerank:
    print(f"\n❌ CON_2024_004 ELIMINADO por re-ranking")
    print("\nTop-10 post-rerank:")
    for i, chunk in enumerate(chunks_reranked, 1):
        print(f"  {i}. {chunk.get('metadata', {}).get('source', 'unknown')}")


# PASO 4: RAG completo
print("\n" + "="*80)
print("PASO 4: RESPUESTA RAG")
print("="*80)
response = chat(QUERY, [])
print(f"\n📄 {response[:500]}...\n")

# CONCLUSIÓN
print("\n" + "="*80)
print("🎯 DIAGNÓSTICO")
print("="*80)
print(f"\n1. CON_2024_004 en retrieval? {'✅' if found_004 else '❌'}")
print(f"2. CON_2024_004 en top-10 reranked? {'✅' if found_004_rerank else '❌'}")
print(f"3. Respuesta correcta? {'✅' if 'CON_2024_004' in response else '❌'}")

if not found_004:
    print("\n⚠️ PROBLEMA: RETRIEVAL - chunk no recuperado")
elif not found_004_rerank:
    print("\n⚠️ PROBLEMA: RE-RANKING - BGE lo elimina")
else:
   print("\n⚠️ PROBLEMA: PROMPT LLM - ignora chunk correcto")
