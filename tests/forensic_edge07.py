# -*- coding: utf-8 -*-
"""
ANÁLISIS FORENSE: EDGE_07
¿Qué contratos comparten un hito de ejecución fijado para el 16/12/2024?
Expected: CON_2024_004, CON_2024_007, SER_2024_008, SER_2024_019
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.hybrid_search import hybrid_search
from src.agents.rag_agent import chat

QUERY = "¿Qué contratos comparten un hito de ejecución fijado para el 16/12/2024?"
EXPECTED = ["CON_2024_004", "CON_2024_007", "SER_2024_008", "SER_2024_019"]
TARGET_DATE = "16/12/2024"

print("="*80)
print("🔬 ANÁLISIS FORENSE: EDGE_07")
print("="*80)
print(f"\n📝 Query: {QUERY}")
print(f"✅ Expected ({len(EXPECTED)}): {', '.join(EXPECTED)}\n")

# Hybrid search
chunks_raw = hybrid_search(QUERY, top_k=30, filter_metadata=None)

# Buscar fecha específica en chunks
print(f"\n🎯 BÚSQUEDA DE '{TARGET_DATE}' EN CHUNKS:")
contracts_with_date = []

for i, chunk in enumerate(chunks_raw, 1):
    content = chunk.get('contenido', '')
    source = chunk.get('metadata', {}).get('source', 'unknown')
    
    if TARGET_DATE in content or "16/12/2024" in content or "16-12-2024" in content:
        # Extraer contract ID
        import re
        contract_match = re.search(r'(CON|SER|SUM|LIC)_\d{4}_\d{3}', source)
        if contract_match:
            contract_id = contract_match.group(0)
            if contract_id not in contracts_with_date:
                contracts_with_date.append(contract_id)
                marker = "✅" if contract_id in EXPECTED else "⚠️"
                print(f"\n{marker} Posición #{i}: {contract_id}")
                print(f"   Snippet: {content[:200]}...")

print(f"\n📊 CONTRATOS CON FECHA '{TARGET_DATE}' EN CHUNKS:")
print(f"   Encontrados: {len(contracts_with_date)}")
print(f"   IDs: {', '.join(contracts_with_date)}")

# Ver qué esperados NO se encontraron
missing = [c for c in EXPECTED if c not in contracts_with_date]
if missing:
    print(f"\n❌ CONTRATOS ESPERADOS NO ENCONTRADOS:")
    for m in missing:
        print(f"   - {m}")

# Respuesta RAG
print("\n" + "="*80)
print("RESPUESTA RAG")
print("="*80)
response = chat(QUERY, [])
print(f"\n📄 {response[:600]}...\n")

# Diagnóstico
found_in_response = [c for c in EXPECTED if c in response]
print(f"\n🎯 DIAGNÓSTICO:")
print(f"Esperados: {len(EXPECTED)} contratos")
print(f"En chunks: {len(contracts_with_date)} contratos")
print(f"En respuesta: {len(found_in_response)} contratos")
print(f"\nRespuesta menciona: {', '.join(found_in_response) if found_in_response else 'NINGUNO'}")

omitted = [c for c in EXPECTED if c not in found_in_response]
if omitted:
    print(f"Omitidos por LLM: {', '.join(omitted)}")
