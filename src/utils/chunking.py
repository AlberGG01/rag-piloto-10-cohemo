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
    Extrae metadata del contenido del PDF usando regex.
    """
    metadata = {
        "archivo": filename,
        "num_contrato": None,
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
        "nivel_seguridad": "SIN CLASIFICAR",
        "normas": None
    }
    
    # 1. NÚMERO DE EXPEDIENTE / CONTRATO
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
            
    # Fallback al nombre del archivo si falla regex
    if not metadata["num_contrato"]:
         # Ejemplo: CON_2024_001_Suministro.pdf -> CON_2024_001
         parts = filename.split('_')
         if len(parts) >= 3 and parts[0] in ["CON", "SER", "SUM", "LIC"]:
             metadata["num_contrato"] = f"{parts[0]}_{parts[1]}_{parts[2]}"

    # 2. IMPORTE (Búsqueda robusta)
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
            # Validar que parece un número
            if any(c.isdigit() for c in val):
                metadata["importe"] = val + " EUR"
                break

    # 3. FECHAS CLAVE
    date_pattern = r"\b(\d{1,2}/\d{1,2}/\d{4})\b"
    dates = re.findall(date_pattern, text)
    if dates:
        # Heurística simple: Primera fecha suele ser firma/inicio, última vencimiento (muy falible pero útil)
        # Mejor buscar contexto
        pass # Se hará mejor en el chunking individual o con regex específico
        
    # Regex específicos para fechas
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

    # 4. AVALES
    aval_entidad_patterns = [
        r"Entidad avalista:\s*(.+?)(?:\n|$)",
        r"Avalado por:\s*(.+?)(?:\n|$)",
        r"Banco:\s*(.+?)(?:\n|$)"
    ]
    for pattern in aval_entidad_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            entidad = match.group(1).strip()
            # Limpieza básica
            if len(entidad) < 50: 
                metadata["aval_entidad"] = entidad
                break
                
    # 5. NORMATIVA (STANAG, ISO)
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
