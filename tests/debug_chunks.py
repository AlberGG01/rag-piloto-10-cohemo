# -*- coding: utf-8 -*-
"""
Debug Chunks Recuperados - Ver exactamente QUÉ se está recuperando
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.hierarchical_retrieval import hierarchical_retrieval

def debug_retrieved_chunks():
    """Ver exactamente qué chunks se recuperan para AGG001."""
    
    query = "¿Cuál es el importe total acumulado de todos los avales bancarios en el sistema?"
    
    print("\n" + "="*80)
    print(f"QUERY: {query}")
    print("="*80)
    
    chunks = hierarchical_retrieval(query, top_docs=15, chunks_per_doc=3)
    
    print(f"\nTotal chunks recuperados: {len(chunks)}")
    print(f"Documentos únicos: {len(set(c['metadata'].get('archivo', '')[:16] for c in chunks))}")
    
    print("\n" + "="*80)
    print("ANÁLISIS DE CHUNKS")
    print("="*80)
    
    count_con_aval = 0
    count_con_garantia = 0
    count_con_importe = 0
    
    for i, chunk in enumerate(chunks, 1):
        archivo = chunk['metadata'].get('archivo', 'N/A')[:30]
        seccion = chunk['metadata'].get('seccion', 'N/A')
        contenido = chunk.get('contenido', '')
        
        tiene_aval = 'aval' in contenido.lower()
        tiene_garantia = 'garantía' in contenido.lower() or 'garantia' in contenido.lower()
        tiene_importe = any(word in contenido.lower() for word in ['eur', '€', '.000,00', ',00 eur'])
        
        if tiene_aval: count_con_aval += 1
        if tiene_garantia: count_con_garantia += 1
        if tiene_importe: count_con_importe += 1
        
        print(f"\n[Chunk {i}]")
        print(f"  Archivo: {archivo}")
        print(f"  Sección: {seccion}")
        print(f"  Score RRF: {chunk['metadata'].get('rrf_score', 'N/A')}")
        print(f"  Tiene 'aval': {'✓' if tiene_aval else '✗'}")
        print(f"  Tiene 'garantía': {'✓' if tiene_garantia else '✗'}")
        print(f"  Tiene importe: {'✓' if tiene_importe else '✗'}")
        print(f"  Contenido (primeros 200 chars):")
        print(f"    {contenido[:200]}...")
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"Chunks con 'aval': {count_con_aval}/{len(chunks)} ({count_con_aval/len(chunks)*100:.1f}%)")
    print(f"Chunks con 'garantía': {count_con_garantia}/{len(chunks)} ({count_con_garantia/len(chunks)*100:.1f}%)")
    print(f"Chunks con importe: {count_con_importe}/{len(chunks)} ({count_con_importe/len(chunks)*100:.1f}%)")
    
    print("\n" + "="*80)
    print("DIAGNÓSTICO")
    print("="*80)
    
    if count_con_garantia < len(chunks) * 0.5:
        print("❌ PROBLEMA: Menos del 50% de chunks contienen información de garantías")
        print("→ El scoring NO está priorizando chunks correctos")
        print("→ Solución: Query expansion o metadata filtering")
    else:
        print("✓ Chunks parecen contener información relevante")
        print("→ El problema probablemente es LLM extracción")

if __name__ == "__main__":
    debug_retrieved_chunks()
