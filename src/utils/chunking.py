# -*- coding: utf-8 -*-
"""
Chunking de documentos PDF/Markdown con contexto inteligente.
Usa RecursiveCharacterTextSplitter de LangChain para chunks semánticos.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.utils.pdf_processor import load_pdf_documents

logger = logging.getLogger(__name__)

# Configuración del Text Splitter
from src.config import CHUNK_MAX_TOKENS, CHUNK_OVERLAP


def load_markdown_document(md_path: Path) -> List[Document]:
    """
    Carga un archivo Markdown normalizado como Document de LangChain.
    
    Args:
        md_path: Ruta al archivo .md
    
    Returns:
        Lista con un solo Document (Markdown no tiene páginas)
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Crear Document único con todo el contenido
        doc = Document(
            page_content=content,
            metadata={"source": md_path.name, "page": 1}
        )
        
        logger.info(f"✅ Markdown cargado: {md_path.name} ({len(content)} chars)")
        return [doc]
        
    except Exception as e:
        logger.error(f"Error cargando markdown {md_path.name}: {e}")
        return []


# Definir splitter global eficiente
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,  # ~300-400 tokens
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)

def extract_metadata_from_text(text: str, filename: str) -> Dict:
    """
    Extrae metadata del contenido del PDF o Markdown normalizado usando regex.
    """
    metadata = {
        "archivo": filename,
        "num_contrato": None,
        "num_expediente": None, # Alias para el analizador
        "tipo_contrato": None,
        "contratante": None,
        "contratista": None,
        "fecha_inicio": None,
        "fecha_fin": None,
        "importe": None,
        "aval_vencimiento": None,
        "aval_importe": None,
        "aval_entidad": None,
        "requiere_confidencialidad": False,
        "permite_revision_precios": True, # Por defecto True si no se encuentra
        "nivel_seguridad": "SIN CLASIFICAR",
        "normas": None,
        "hitos_entrega": []
    }
    
    # --- 1. NÚMERO DE EXPEDIENTE / CONTRATO ---
    # Patrones para Markdown normalizado
    exp_md = re.search(r"\*\*Expediente:\*\*\s*([A-Z0-9_\-]+)", text)
    if exp_md:
        metadata["num_contrato"] = exp_md.group(1).strip()
    else:
        # Patrones clásicos PDF
        exp_patterns = [
            r"EXPEDIENTE:\s*([A-Z0-9_\-]+)",
            r"Expediente:\s*([A-Z0-9_\-]+)",
            r"Nº Expediente:\s*([A-Z0-9_\-]+)",
            r"([A-Z]{2,4}_\d{4}_\d{3})"
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text)
            if match:
                metadata["num_contrato"] = match.group(1).strip()
                break
    
    metadata["num_expediente"] = metadata["num_contrato"] # Sincronizar
            
    # Fallback al nombre del archivo si falla regex
    if not metadata["num_contrato"]:
         parts = filename.split('_')
         if len(parts) >= 3 and parts[0] in ["CON", "SER", "SUM", "LIC"]:
             metadata["num_contrato"] = f"{parts[0]}_{parts[1]}_{parts[2]}"
             metadata["num_expediente"] = metadata["num_contrato"]

    # --- 2. IMPORTE ---
    # Markdown
    imp_md = re.search(r"\*\*Importe [Tt]otal.*?\*\*:\s*([\d\.,]+\s*EUR)", text)
    if imp_md:
        metadata["importe"] = imp_md.group(1).strip()
    else:
        importe_patterns = [
            r"Importe total:\s*([\d\.,]+)\s*(?:€|EUR)",
            r"Importe de adjudicación:\s*([\d\.,]+)\s*(?:€|EUR)",
            r"Valor estimado:\s*([\d\.,]+)\s*(?:€|EUR)",
            r"Precio:\s*([\d\.,]+)\s*(?:€|EUR)"
        ]
        for pattern in importe_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                val = match.group(1).replace(" ", "")
                if any(c.isdigit() for c in val):
                    metadata["importe"] = val + " EUR"
                    break

    # --- 3. FECHAS CLAVE ---
    # Fecha Fin (Markdown)
    fin_md = re.search(r"\*\*Fecha Fin:\*\*\s*(\d{1,2}/\d{1,2}/\d{4})", text)
    if fin_md:
        metadata["fecha_fin"] = fin_md.group(1)
    else:
        fin_patterns = [
            r"Fecha de finalización:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Vigencia hasta el:\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Plazo de ejecución:.*hasta el (\d{1,2}/\d{1,2}/\d{4})"
        ]
        for pattern in fin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["fecha_fin"] = match.group(1)
                break

    # --- 4. AVALES ---
    # Fecha Vencimiento Aval (Markdown)
    aval_v_md = re.search(r"\*\*Fecha de vencimiento del aval:\*\*\s*(\d{1,2}/\d{1,2}/\d{4})", text)
    if aval_v_md:
        metadata["aval_vencimiento"] = aval_v_md.group(1)
    
    # Importe Aval (Markdown)
    aval_imp_md = re.search(r"\*\*Garantía definitiva:\*\*\s*([\d\.,]+\s*EUR)", text)
    if aval_imp_md:
        metadata["aval_importe"] = aval_imp_md.group(1)

    # Entidad Avalista
    aval_e_md = re.search(r"\*\*Entidad avalista:\*\*\s*(.*)", text)
    if aval_e_md:
        metadata["aval_entidad"] = aval_e_md.group(1).strip()
    else:
        aval_entidad_patterns = [
            r"Entidad avalista:\s*(.+?)(?:\n|$)",
            r"Avalado por:\s*(.+?)(?:\n|$)",
            r"Banco:\s*(.+?)(?:\n|$)"
        ]
        for pattern in aval_entidad_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entidad = match.group(1).strip()
                if len(entidad) < 50: 
                    metadata["aval_entidad"] = entidad
                    break

    # --- 5. CONDICIONES ESPECIALES ---
    # Confidencialidad
    conf_md = re.search(r"\*\*Cláusula de confidencialidad:\*\*\s*(.*)", text)
    if conf_md and len(conf_md.group(1)) > 5:
        metadata["requiere_confidencialidad"] = True
        # Nivel seguridad
        nivel_md = re.search(r"\*\*Clasificación de seguridad:\*\*\s*([A-Z]+)", text)
        if nivel_md:
            metadata["nivel_seguridad"] = nivel_md.group(1)
            
    # Revisión de Precios
    rev_md = re.search(r"\*\*Revisión de precios:\*\*\s*([Ss]í|[Nn]o)", text)
    if rev_md:
        metadata["permite_revision_precios"] = "sí" in rev_md.group(1).lower()

    # --- 6. NORMATIVA ---
    normas_patterns = [
        r"(STANAG\s*\d+)",
        r"(ISO\s*\d+[:\-]?\d*)",
        r"(MIL-STD-\d+[A-Z]?)",
        r"(PECAL\s*\d+)",
        r"(UNE-EN\s*\d+)"
    ]
    found_normas = []
    for pattern in normas_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found_normas.extend(matches)
    
    if found_normas:
        metadata["normas"] = ", ".join(sorted(list(set(n.upper() for n in found_normas))))

    return metadata


def create_chunks_from_pdf(file_path: Path) -> List[Dict]:
    """
    Crea chunks desde un archivo PDF o Markdown normalizado.
    Detecta automáticamente el formato por la extensión.
    
    Args:
        file_path: Ruta al archivo (.pdf o .md)
    
    Returns:
        Lista de chunks con 'contenido' y 'metadata'
    """
    # Detectar tipo de archivo
    if file_path.suffix.lower() == '.md':
        raw_docs = load_markdown_document(file_path)
    elif file_path.suffix.lower() == '.pdf':
        raw_docs = load_pdf_documents(file_path)
    else:
        logger.error(f"❌ Formato no soportado: {file_path.suffix}")
        return []
    
    if not raw_docs:
        logger.warning(f"⚠️ No se pudieron cargar documentos de {file_path.name}")
        return []
    
    # Extraer Texto Completo para Metadata Global
    full_text = "\n".join([d.page_content for d in raw_docs])
    global_meta = extract_metadata_from_text(full_text, file_path.name)
    
    processed_chunks = []
    
    # Procesar iterativamente con contexto de página/sección
    for doc in raw_docs:
        # Detectar si es un ANEXO por el contenido
        is_anexo = False
        section_label = "Cuerpo_Principal"
        
        header_text = doc.page_content[:200].upper()
        if "ANEXO" in header_text or "APÉNDICE" in header_text:
            is_anexo = True
            section_label = "Anexo"
            # Intentar extraer "Anexo I", "Anexo A"
            match = re.search(r"(ANEXO\s+[A-Z0-9]+)", header_text)
            if match:
                section_label = match.group(1)
        
        # Split de la página/documento
        chunks = text_splitter.split_text(doc.page_content)
        
        for i, chunk_text in enumerate(chunks):
            # Construir metadatos finales
            chunk_meta = global_meta.copy()
            chunk_meta.update({
                "source": file_path.name,
                "pagina": doc.metadata.get("page", 1),
                "seccion": section_label,
                "chunk_index": i
            })
            
            processed_chunks.append({
                "contenido": chunk_text,
                "metadata": chunk_meta
            })
            
    logger.info(f"Procesado {file_path.name}: {len(processed_chunks)} chunks.")
    return processed_chunks


def create_all_chunks() -> List[Dict]:
    """
    Procesa TODOS los contratos disponibles y genera chunks.
    Usa por defecto la configuración de usar archivos normalizados si existen.
    """
    from src.utils.pdf_processor import get_all_contracts
    
    files = get_all_contracts(use_normalized=True) # Preferir Markdown si hay
    all_chunks = []
    
    for f in files:
        chunks = create_chunks_from_pdf(f)
        all_chunks.extend(chunks)
        
    logger.info(f"Total global: {len(all_chunks)} chunks generados de {len(files)} archivos.")
    return all_chunks
