"""
Diagnóstico completo de VectorDB
"""
import sys
import os

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import actual available functions
try:
    from src.utils.vectorstore import get_collection, search as vector_search
    # Try importing hybrid search if available, else fallback
    try:
        from src.utils.hybrid_search import hybrid_search
        SEARCH_FUNC = hybrid_search
        SEARCH_NAME = "Hybrid Search"
    except ImportError:
        SEARCH_FUNC = vector_search
        SEARCH_NAME = "Vector Search"

except ImportError as e:
    print(f"🚨 CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

def diagnose_vectordb():
    print("="*60)
    print("🔍 DIAGNÓSTICO VECTORDB")
    print("="*60)
    
    try:
        collection = get_collection()
    except Exception as e:
        print(f"🚨 ERROR: No se pudo cargar collection: {e}")
        return

    # 1. Count total
    try:
        total = collection.count()
        print(f"\n📊 Total chunks indexados: {total}")
    except Exception as e:
        print(f"🚨 ERROR al contar chunks: {e}")
        return
    
    if total == 0:
        print("🚨 ERROR CRÍTICO: VectorDB vacía")
        return
    
    # 2. Sample metadata
    try:
        sample = collection.get(limit=10)
        print(f"\n📋 Sample de metadatos:")
        if sample and 'metadatas' in sample and sample['metadatas']:
            for i, meta in enumerate(sample['metadatas'][:5], 1):
                clean_meta = {k: v for k, v in meta.items() if k != 'embedding'} # hide embedding if present
                print(f"  {i}. {clean_meta}")
        else:
            print("  (No metadatas found in sample)")
    except Exception as e:
        print(f"🚨 ERROR al obtener sample: {e}")
    
    # 3. Test retrieval de queries FALLIDAS
    failed_tests = [
        ("CIF ciberseguridad CON_2024_004", "B-55667788"),
        ("ISO 18788 vigilancia", "ISO 18788"),
        ("fecha retamares ejecución", "12/10/2027")
    ]
    
    print(f"\n🧪 Test de Retrieval en Queries Fallidas (Usando {SEARCH_NAME}):")
    for query, expected in failed_tests:
        try:
            # Search returns list of chunks
            if SEARCH_NAME == "Hybrid Search":
                 chunks = SEARCH_FUNC(query, top_k=50) # hybrid args
            else:
                 chunks = SEARCH_FUNC(query, k=50) # vector args
            
            if not chunks:
                 print(f"  ❌ '{expected[:30]}...' → NO CHUNKS RETURNED")
                 continue

            found = any(expected in c.get('contenido', '') for c in chunks)
            pos = next((i for i, c in enumerate(chunks, 1) if expected in c.get('contenido', '')), None)
            
            status = "SUCCESS" if found and pos <= 15 else "WARNING" if found else "FAILURE"
            print(f"  {status} '{expected[:30]}...' -> {'Pos #'+str(pos) if found else 'NOT FOUND'}")
        except Exception as e:
             print(f"  FAILURE Error retrieving for query '{query}': {e}")
    
    # 4. Verificar archivos fuente
    try:
        archivos_unicos = set()
        # Use collection get directly for metadatas
        all_data = collection.get(include=['metadatas']) 
        if all_data and 'metadatas' in all_data:
            for meta in all_data['metadatas']:
                fname = meta.get('archivo') or meta.get('source')
                if fname:
                    archivos_unicos.add(fname)
        
        print(f"\n FILES Unique indexed files: {len(archivos_unicos)}")
        print(f"   Sample: {list(archivos_unicos)[:5]}")
    except Exception as e:
        print(f" ERROR verifying source files: {e}")

if __name__ == "__main__":
    diagnose_vectordb()
