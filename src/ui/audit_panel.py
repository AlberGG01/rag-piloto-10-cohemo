import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import NORMALIZED_PATH
from src.utils.chunking import create_chunks_from_text
from src.utils.vectorstore import add_documents

# Config
REVIEW_FILE = "pending_review.json"

st.set_page_config(page_title="🛡️ Integrity Audit Panel", layout="wide")

st.title("🛡️ Supervisor Audit Panel (HITL)")

def load_pending_reviews():
    if not os.path.exists(REVIEW_FILE):
        return []
    try:
        with open(REVIEW_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_pending_reviews(reviews):
    with open(REVIEW_FILE, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

def index_corrected_document(filename, content, metadata):
    """
    Guarda el MD corregido e indexa.
    """
    # 1. Guardar Markdown corrigido
    file_path = NORMALIZED_PATH / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    st.info(f"💾 Archivo {filename} actualizado en disco.")
    
    # 2. Indexar
    st.info("🔄 Generando chunks e indexando...")
    chunks = create_chunks_from_text(content, {
        "source": filename,
        **metadata
    })
    
    if chunks:
        added = add_documents(chunks)
        st.success(f"✅ Documento indexado exitosamente ({len(chunks)} chunks).")
        return True
    else:
        st.error("❌ Error creando chunks.")
        return False

# ----- MAIN UI -----

reviews = load_pending_reviews()

if not reviews:
    st.success("✅ No hay documentos pendientes de revisión. Sistema limpio.")
    st.stop()

# Sidebar List
st.sidebar.header(f"Pendientes ({len(reviews)})")
selected_idx = st.sidebar.radio(
    "Seleccionar Documento:", 
    range(len(reviews)), 
    format_func=lambda i: f"{reviews[i]['filename']} (Score: {reviews[i]['audit_result']['integrity_score']})"
)

item = reviews[selected_idx]
audit = item['audit_result']
filename = item['filename']

st.subheader(f"📝 Revisando: {filename}")

# Status Banner
st.error(f"🚨 Motivo de Bloqueo: {audit.get('detected_errors', ['Unknown Error'])}")

# Layout: Comparison (Left) & Form (Right)
col_preview, col_form = st.columns([1, 1])

with col_preview:
    st.markdown("### 📄 Contenido Detectado")
    # Show preview snippet or full content if we could load it (here using snippet from log)
    st.text_area("Vista Previa (Snippet)", item.get('preview_snippet', ''), height=400, disabled=True)
    st.caption("Nota: Para edición completa, el sistema requeriría cargar el archivo original. Aquí mostramos el fragmento problemático.")

with col_form:
    st.markdown("### 🛠️ Corrección Manual")
    
    with st.form("correction_form"):
        meta = audit.get('metadata', {})
        
        new_id = st.text_input("ID Contrato", value=meta.get('id_contrato', ''))
        new_adj = st.text_input("Adjudicatario", value=meta.get('adjudicatario', ''))
        new_imp = st.text_input("Importe Total", value=meta.get('importe_total', ''))
        new_obj = st.text_area("Objeto", value=meta.get('objeto', ''))
        
        st.warning("⚠️ Al aprobar, se sobrescribirá el archivo y se forzará la indexación.")
        
        if st.form_submit_button("✅ Autorizar e Indexar"):
            
            # Construct full markdown (Mock recreation for this demo since we only have snippet)
            # In production, we'd read the full file.
            # Assuming we fix the header:
            
            fixed_content = f"""# {new_id}
**Adjudicatario**: {new_adj}
**Importe**: {new_imp}
**Objeto**: {new_obj}

{item.get('preview_snippet', '')}
"""
            
            # Index Logic
            if index_corrected_document(filename, fixed_content, {
                "id_contrato": new_id,
                "adjudicatario": new_adj,
                "importe": new_imp
            }):
                # Remove from queue
                reviews.pop(selected_idx)
                save_pending_reviews(reviews)
                st.rerun()

    if st.button("🗑️ Descartar Documento (Ignorar)"):
        reviews.pop(selected_idx)
        save_pending_reviews(reviews)
        st.warning("Documento descartado de la cola.")
        st.rerun()
