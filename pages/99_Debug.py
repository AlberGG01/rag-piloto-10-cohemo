
import streamlit as st
import sys
from pathlib import Path

# Configuración de path raíz
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.vectorstore import get_collection

st.set_page_config(layout="wide")
st.title("🛠️ Diagnóstico de ChromaDB")

if st.button("Ejecutar Diagnóstico"):
    with st.spinner("Conectando a base de datos..."):
        try:
            collection = get_collection()
            if not collection:
                st.error("❌ No se pudo conectar a ChromaDB")
                st.stop()
                
            count = collection.count()
            st.metric("Total Chunks", count)
            
            if count == 0:
                st.warning("⚠️ Colección vacía")
                st.stop()
                
            st.info("Recuperando metadatos (limit=5000)...")
            result = collection.get(include=["metadatas"], limit=5000)
            metadatas = result.get("metadatas", [])
            
            unique_files = set()
            file_counts = {}
            
            for meta in metadatas:
                fname = meta.get("archivo") or meta.get("source") or meta.get("filename") or "DESCONOCIDO"
                unique_files.add(fname)
                file_counts[fname] = file_counts.get(fname, 0) + 1
            
            st.subheader(f"Documentos Indexados ({len(unique_files)})")
            
            # Convertir a lista de tuplas para tabla
            data = []
            found_vehiculos = False
            
            for fname in sorted(unique_files):
                is_target = "vehiculo" in fname.lower() or "blindado" in fname.lower()
                if is_target:
                    found_vehiculos = True
                    fname_display = f"🎯 **{fname}**"
                    print(f"DEBUG: Found target file: {fname}")
                else:
                    fname_display = fname
                    print(f"DEBUG: File: {fname}")
                    
                data.append({
                    "Nombre de Archivo": fname_display,
                    "Chunks": file_counts[fname],
                    "Estado": "✅ Encontrado" if is_target else "Normal"
                })
            
            print(f"DEBUG: Total Unique Files: {len(unique_files)}")
            print(f"DEBUG: Found Vehiculos: {found_vehiculos}")
                
            st.write(data)
            
            if found_vehiculos:
                st.success("✅ CONFIRMADO: El contrato de Vehículos Blindados ESTÁ en el índice.")
            else:
                st.error("❌ ALERTA: NO se encuentra el contrato de Vehículos Blindados.")
                
        except Exception as e:
            st.error(f"Error crítico: {str(e)}")
