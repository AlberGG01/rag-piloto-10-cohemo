# -*- coding: utf-8 -*-
"""
Debug RAG - Muestra internamente qué está pasando
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.vectorstore import search as vector_search
from src.utils.hybrid_search import hybrid_search
from src.utils.reranker import rerank_with_llm
from src.utils.llm_config import generate_response
from src.config import EXTRACTOR_PROMPT, RESPONDER_PROMPT

def debug_query(query: str):
    """
    Debugging completo de una query mostrando cada paso.
    """
    print("\n" + "="*80)
    print(f"DEBUG QUERY: {query}")
    print("="*80)
    
    # PASO 1: Vector Search Solo
    print("\n[PASO 1] VECTOR SEARCH (solo vectorial)")
    print("-" * 80)
    vector_results = vector_search(query, k=10)
    print(f"Chunks recuperados: {len(vector_results)}")
    for i, chunk in enumerate(vector_results[:3], 1):
        print(f"\n  [{i}] Score: {chunk.get('distancia', 'N/A')}")
        print(f"      Contrato: {chunk['metadata'].get('num_contrato', 'N/A')}")
        print(f"      Contenido: {chunk['contenido'][:150]}...")
    
    # PASO 2: Hybrid Search (Vector + BM25)
    print("\n\n[PASO 2] HYBRID SEARCH (Vector + BM25 + RRF)")
    print("-" * 80)
    try:
        hybrid_results = hybrid_search(query, top_k=10)
        print(f"Chunks recuperados: {len(hybrid_results)}")
        for i, chunk in enumerate(hybrid_results[:3], 1):
            print(f"\n  [{i}] RRF Score: {chunk['metadata'].get('rrf_score', 'N/A')}")
            print(f"      Contrato: {chunk['metadata'].get('num_contrato', 'N/A')}")
            print(f"      Contenido: {chunk['contenido'][:150]}...")
    except Exception as e:
        print(f"ERROR en hybrid search: {e}")
        hybrid_results = vector_results[:10]
    
    # PASO 3: Re-ranking con LLM
    print("\n\n[PASO 3] RE-RANKING CON LLM")
    print("-" * 80)
    try:
        reranked = rerank_with_llm(query, hybrid_results, top_k=5)
        print(f"Chunks finales: {len(reranked)}")
        for i, chunk in enumerate(reranked, 1):
            print(f"\n  [{i}] Rerank Score: {chunk['metadata'].get('rerank_score', 'N/A')}")
            print(f"      Contrato: {chunk['metadata'].get('num_contrato', 'N/A')}")
            print(f"      Contenido: {chunk['contenido'][:150]}...")
    except Exception as e:
        print(f"ERROR en re-ranking: {e}")
        reranked = hybrid_results[:5]
    
    # PASO 4: Extracción con LLM
    print("\n\n[PASO 4] EXTRACCION CON LLM (Paso 1: Extractor)")
    print("-" * 80)
    
    # Preparar contexto
    context = "\n\n---\n\n".join([
        f"[Documento {i+1}]\n{chunk['contenido']}"
        for i, chunk in enumerate(reranked)
    ])
    
    extractor_prompt = EXTRACTOR_PROMPT.format(
        pregunta=query,
        contexto=context,
        historial=""
    )
    
    print(f"Prompt Extractor (primeros 500 chars):")
    print(extractor_prompt[:500] + "...")
    
    try:
        datos_extraidos = generate_response(extractor_prompt, max_tokens=600, temperature=0.0)
        print(f"\nDatos extraídos por LLM:")
        print(datos_extraidos[:500] + "..." if len(datos_extraidos) > 500 else datos_extraidos)
    except Exception as e:
        print(f"ERROR en extracción: {e}")
        datos_extraidos = "ERROR"
    
    # PASO 5: Generación Final
    print("\n\n[PASO 5] GENERACION FINAL (Paso 2: Responder)")
    print("-" * 80)
    
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    
    responder_prompt = RESPONDER_PROMPT.format(
        fecha_actual=fecha_actual,
        datos_extraidos=datos_extraidos,
        pregunta=query,
        historial=""
    )
    
    print(f"Prompt Responder (primeros 500 chars):")
    print(responder_prompt[:500] + "...")
    
    try:
        respuesta_final = generate_response(responder_prompt, max_tokens=700, temperature=0.0)
        print(f"\nRespuesta Final:")
        print(respuesta_final)
    except Exception as e:
        print(f"ERROR en generación final: {e}")
        respuesta_final = "ERROR"
    
    # RESUMEN
    print("\n\n" + "="*80)
    print("RESUMEN DEL DEBUGGING")
    print("="*80)
    print(f"1. Vector search: {len(vector_results)} chunks")
    print(f"2. Hybrid search: {len(hybrid_results)} chunks")
    print(f"3. Re-ranking: {len(reranked)} chunks finales")
    print(f"4. Extracción: {'OK' if 'ERROR' not in datos_extraidos else 'FALLO'}")
    print(f"5. Generación: {'OK' if 'ERROR' not in respuesta_final else 'FALLO'}")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # Debuggear pregunta de agregación que falló
    debug_query("¿Cuál es el importe total acumulado de todos los avales bancarios en el sistema?")
