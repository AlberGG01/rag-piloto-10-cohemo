# -*- coding: utf-8 -*-
"""
Análisis de Chunking - Diagnóstico CRÍTICO
"""

import sys
from pathlib import Path
from collections import defaultdict
import statistics

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.vectorstore import get_collection

def analyze_chunking():
    """Analiza distribución de chunks por documento."""
    
    collection = get_collection()
    all_data = collection.get(include=['metadatas'])
    
    chunks_per_doc = defaultdict(int)
    
    for metadata in all_data['metadatas']:
        # Metadata tiene 'archivo', no 'num_contrato'
        doc_id = metadata.get('archivo', 'UNKNOWN')
        if doc_id != 'UNKNOWN':
            # Extraer código de contrato del nombre de archivo
            # "CON_2024_001_..." -> "CON_2024_001"
            doc_code = '_'.join(doc_id.split('_')[:3]) if '_' in doc_id else doc_id
            chunks_per_doc[doc_code] += 1
    
    values = list(chunks_per_doc.values())
    
    print("\n" + "="*80)
    print("ANÁLISIS DE CHUNKING")
    print("="*80)
    
    print(f"\nTotal documentos: {len(chunks_per_doc)}")
    print(f"Total chunks: {sum(values)}")
    print(f"\nDistribución de chunks por documento:")
    print(f"  Mínimo: {min(values)} chunks")
    print(f"  Máximo: {max(values)} chunks")
    print(f"  Media: {statistics.mean(values):.1f} chunks")
    print(f"  Mediana: {statistics.median(values):.1f} chunks")
    print(f"  Desv. Estándar: {statistics.stdev(values):.1f}")
    
    # Identificar outliers
    outliers_low = {k:v for k,v in chunks_per_doc.items() if v < 5}
    outliers_high = {k:v for k,v in chunks_per_doc.items() if v > 20}
    
    if outliers_high:
        print(f"\n⚠️  Documentos muy fragmentados (>20 chunks):")
        for doc, count in sorted(outliers_high.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {doc}: {count} chunks")
    
    if outliers_low:
        print(f"\n⚠️  Documentos poco fragmentados (<5 chunks):")
        for doc, count in sorted(outliers_low.items(), key=lambda x: x[1]):
            print(f"  - {doc}: {count} chunks")
    
    # Calcular balance
    cv = (statistics.stdev(values) / statistics.mean(values)) * 100
    print(f"\nCoeficiente de Variación: {cv:.1f}%")
    
    if cv < 30:
        print("✅ Chunking BALANCEADO - MMR es suficiente")
        strategy = "MMR"
    elif cv < 50:
        print("⚠️  Chunking MODERADAMENTE DESBALANCEADO - Considerar retrieval jerárquico")
        strategy = "HYBRID"
    else:
        print("❌ Chunking MUY DESBALANCEADO - REQUIERE retrieval jerárquico")
        strategy = "HIERARCHICAL"
    
    # Análisis de cobertura
    print(f"\n" + "="*80)
    print("ANÁLISIS DE COBERTURA")
    print("="*80)
    
    total_docs = len(chunks_per_doc)
    
    for top_k in [10, 20, 30, 50]:
        # Simulación: si recupero top_k chunks al azar
        # ¿Cuántos documentos únicos esperaría?
        avg_chunks = statistics.mean(values)
        expected_docs = min(top_k / avg_chunks, total_docs)
        coverage = (expected_docs / total_docs) * 100
        
        print(f"\ntop_k={top_k}:")
        print(f"  Documentos únicos esperados: {expected_docs:.1f}")
        print(f"  Cobertura: {coverage:.1f}%")
        
        if top_k == 50:
            print(f"  → Para 200 docs: {expected_docs * 10:.0f} docs únicos ({coverage:.1f}%)")
    
    print(f"\n" + "="*80)
    print(f"ESTRATEGIA RECOMENDADA: {strategy}")
    print("="*80)
    
    return strategy, chunks_per_doc

if __name__ == "__main__":
    strategy, data = analyze_chunking()
