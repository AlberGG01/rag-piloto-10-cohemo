# -*- coding: utf-8 -*-
"""
Script de diagnóstico para analizar por qué fallaron G002 y G009
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.vectorstore import search
from src.agents.rag_agent import retrieve_and_generate

def diagnose_query(query_id, query, expected_answer):
    """Diagnostica por qué falló una query."""
    print(f"\n{'='*80}")
    print(f"🔍 DIAGNÓSTICO: {query_id}")
    print(f"{'='*80}")
    print(f"Pregunta: {query}")
    print(f"Respuesta esperada: {expected_answer}")
    print()
    
    # 1. Ver qué chunks recuperó
    print("📊 PASO 1: Chunks recuperados")
    print("-" * 80)
    chunks = search(query, k=10)
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Chunk {i}] Distancia: {chunk.get('distancia', 'N/A'):.4f}")
        print(f"Contrato: {chunk['metadata'].get('num_contrato', 'N/A')}")
        print(f"Sección: {chunk['metadata'].get('seccion', 'N/A')}")
        print(f"Contenido (primeros 200 chars):")
        print(chunk['contenido'][:200] + "...")
    
    # 2. Buscar si existe la info correcta
    print(f"\n\n📋 PASO 2: ¿Existe '{expected_answer}' en algún chunk?")
    print("-" * 80)
    
    found = False
    for i, chunk in enumerate(chunks, 1):
        # Buscar keywords de la respuesta esperada
        content_lower = chunk['contenido'].lower()
        if any(keyword.lower() in content_lower for keyword in expected_answer.split(',')):
            print(f"✅ ENCONTRADO en Chunk {i}")
            print(f"   Contrato: {chunk['metadata'].get('num_contrato')}")
            print(f"   Fragmento relevante:")
            # Mostrar contexto
            for line in chunk['contenido'].split('\n'):
                if any(kw.lower() in line.lower() for kw in expected_answer.split(',')):
                    print(f"   > {line.strip()}")
            found = True
    
    if not found:
        print("❌ NO ENCONTRADO en los top-10 chunks")
        print("   Posibles causas:")
        print("   - La información no está en los documentos normalizados")
        print("   - Está en un chunk que no fue recuperado (problema de embeddings)")
    
    # 3. Ver qué respondió el RAG completo
    print(f"\n\n💬 PASO 3: Respuesta del RAG completo")
    print("-" * 80)
    result = retrieve_and_generate(query, history=[])
    print(result['response'][:500])
    
    # 4. Conclusión
    print(f"\n\n📌 CONCLUSIÓN")
    print("-" * 80)
    if found:
        print("Causa probable: PROBLEMA DE LLM o PROMPT")
        print("  → La info está en los chunks pero el LLM no la extrae correctamente")
        print("  → Solución: Mejorar prompt de extracción o usar GPT-4o en lugar de GPT-4o-mini")
    else:
        print("Causa probable: PROBLEMA DE RETRIEVAL")
        print("  → Los chunks correctos no están en el top-10")
        print("  → Solución: Fase 2 (hybrid search + re-ranking)")
    
    print("\n")

# Diagnóstico de las 2 preguntas falladas
diagnose_query(
    "G002",
    "¿Qué entidad bancaria emitió el aval para el contrato de mantenimiento de armamento (CON_2024_002)?",
    "CaixaBank, Caixa"
)

diagnose_query(
    "G009",
    "¿Se permite la subcontratación en el contrato de formación de la fragata F-110?",
    "no, prohib, SER_2024_013"
)
