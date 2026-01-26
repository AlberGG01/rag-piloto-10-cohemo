
import sys
import logging
from pathlib import Path

# Configurar path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.utils.vectorstore import get_collection

def diagnose_chroma():
    print("\n🔍 DIAGNÓSTICO DE CHROMADB\n")
    
    try:
        collection = get_collection()
        if not collection:
            print("❌ No se pudo conectar a la colección.")
            return

        count = collection.count()
        print(f"📄 Total de chunks en ChromaDB: {count}")
        
        if count == 0:
            print("⚠️ La colección está vacía.")
            return

        # Recuperar TODOS los metadatos (limitado a 2000 para no explotar)
        print("📥 Recuperando metadatos...")
        result = collection.get(include=["metadatas"], limit=2000)
        metadatas = result.get("metadatas", [])
        
        unique_files = set()
        file_chunk_counts = {}
        
        for meta in metadatas:
            # Buscar nombre de archivo en diferentes campos posibles
            fname = meta.get("archivo") or meta.get("source") or meta.get("filename") or "DESCONOCIDO"
            unique_files.add(fname)
            file_chunk_counts[fname] = file_chunk_counts.get(fname, 0) + 1
            
        print(f"\n📁 Documentos Únicos Indexados ({len(unique_files)}):")
        print("-" * 50)
        found_blindados = False
        
        for fname in sorted(unique_files):
            count = file_chunk_counts[fname]
            marker = "✅"
            if "vehiculo" in fname.lower() or "blindado" in fname.lower():
                marker = "🎯 ENCONTRADO ->"
                found_blindados = True
                
            print(f"{marker} {fname} ({count} chunks)")
            
        print("-" * 50)
        
        if found_blindados:
            print("\n✅ El contrato de Vehículos Blindados ESTÁ en el índice.")
        else:
            print("\n❌ ALERTA CRÍTICA: El contrato de Vehículos Blindados NO aparece en el índice.")

    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")

if __name__ == "__main__":
    diagnose_chroma()
