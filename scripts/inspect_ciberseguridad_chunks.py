"""
Inspecciona todos los chunks del contrato de Ciberseguridad
"""
import sys
import os
import re

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.utils.vectorstore import get_collection
except ImportError as e:
    print(f"🚨 CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

def inspect_contract_chunks():
    """Muestra TODOS los chunks del contrato CON_2024_004"""
    
    try:
        collection = get_collection()
    except Exception as e:
        print(f"🚨 ERROR loading collection: {e}")
        return
    
    print("="*60)
    print("📋 CHUNKS DEL CONTRATO CON_2024_004 (Ciberseguridad)")
    print("="*60)
    
    # Filtrar por metadata using ChromaDB where clause
    try:
        results = collection.get(where={"num_contrato": "CON_2024_004"})
    except Exception as e:
        print(f"🚨 ERROR querying collection: {e}")
        return

    ciberseg_chunks = []
    if results and 'metadatas' in results:
        for i, meta in enumerate(results['metadatas']):
            ciberseg_chunks.append({
                'index': i,
                'metadata': meta,
                'text': results['documents'][i]
            })
    
    print(f"\n📊 Total chunks de CON_2024_004: {len(ciberseg_chunks)}\n")
    
    if len(ciberseg_chunks) == 0:
        print("🚨 PROBLEMA CRÍTICO: Contrato CON_2024_004 NO tiene chunks indexados")
        print("   Causa probable: Archivo no se procesó durante init_vectorstore.py")
        return
    
    # Mostrar cada chunk
    target_cif_clean = "B55667788"
    target_cif_formatted = "B-55667788"
    
    for i, chunk_data in enumerate(ciberseg_chunks, 1):
        print(f"\n--- CHUNK #{i} ---")
        meta = chunk_data['metadata']
        # Remove embedding if it exists just in case
        clean_meta = {k:v for k,v in meta.items() if k!='embedding'}
        print(f"Metadata: {clean_meta}")
        print(f"Texto (primeros 300 chars):")
        print(f"{chunk_data['text'][:300]}...")
        print()
        
        # Buscar CIF en este chunk
        text = chunk_data['text']
        if target_cif_formatted in text or target_cif_clean in text:
            print("  ✅ ¡CIF ENCONTRADO EN ESTE CHUNK!")
        
        # Buscar variantes comunes
        cif_pattern = r'[A-Z]-?\d{8}'
        cifs_found = re.findall(cif_pattern, text)
        if cifs_found:
            print(f"  📌 CIFs detectados: {cifs_found}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    inspect_contract_chunks()
