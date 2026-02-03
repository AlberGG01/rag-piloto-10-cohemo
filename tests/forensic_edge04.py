# -*- coding: utf-8 -*-
"""
ANÁLISIS FORENSE: EDGE_04
¿Cuál es el contrato que contiene mayor densidad de hitos temporales identificados (cerca de 10 fechas)?
Expected: CON_2024_007 o CON_2024_009
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.hybrid_search import hybrid_search
from src.agents.rag_agent import chat
import re

QUERY = "¿Cuál es el contrato que contiene mayor densidad de hitos temporales identificados (cerca de 10 fechas)?"
EXPECTED = ["CON_2024_007", "CON_2024_009"]

print("="*80)
print("🔬 ANÁLISIS FORENSE: EDGE_04")
print("="*80)
print(f"\n📝 Query: {QUERY}")
print(f"✅ Expected: {' o '.join(EXPECTED)}\n")

# Hybrid search
chunks_raw = hybrid_search(QUERY, top_k=10, filter_metadata=None)

# Contar fechas en cada chunk
print("\n📊 ANÁLISIS DE FECHAS POR CONTRATO:")
date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'

contract_dates = {}
for chunk in chunks_raw:
    source = chunk.get('metadata', {}).get('source', 'unknown')
    content = chunk.get('contenido', '')
    
    # Extraer contrato ID
    contract_match = re.search(r'(CON|SER|SUM|LIC)_\d{4}_\d{3}', source)
    if contract_match:
        contract_id = contract_match.group(0)
    else:
        contract_id = source
    
    # Contar fechas
    dates = re.findall(date_pattern, content)
    
    if contract_id not in contract_dates:
        contract_dates[contract_id] = 0
    contract_dates[contract_id] += len(dates)

# Ordenar por densidad de fechas
sorted_contracts = sorted(contract_dates.items(), key=lambda x: x[1], reverse=True)

print("\n🏆 TOP 5 CONTRATOS POR DENSIDAD DE FECHAS:")
for i, (contract, count) in enumerate(sorted_contracts[:5], 1):
    marker = "✅" if any(exp in contract for exp in EXPECTED) else "  "
    print(f"{marker} {i}. {contract}: {count} fechas")

# Respuesta RAG
print("\n" + "="*80)
print("RESPUESTA RAG")
print("="*80)
response = chat(QUERY, [])
print(f"\n📄 {response[:500]}...\n")

# Diagnóstico
found_in_response = [c for c in EXPECTED if c in response]
print(f"\n🎯 DIAGNÓSTICO:")
print(f"Respuesta menciona: {', '.join(found_in_response) if found_in_response else 'NINGUNO de los esperados'}")

if not found_in_response:
    # Ver qué contrato menciona
    for contract, _ in sorted_contracts[:3]:
        if contract in response:
            print(f"⚠️ Respuesta menciona '{contract}' en su lugar")
