# -*- coding: utf-8 -*-
"""
Sistema de chunking para PDFs de contratos.
Divide documentos en chunks con metadata enriquecida.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import SECTION_DELIMITER, CHUNK_MAX_TOKENS, CHUNK_OVERLAP, NORMALIZED_PATH
from src.utils.pdf_processor import read_pdf_with_pages

logger = logging.getLogger(__name__)

# Import metadata enrichment
from src.utils.metadata_enrichment import enrich_chunk_metadata


def extract_metadata_from_text(text: str, filename: str) -> Dict:
    """
    Extrae metadata del contenido del PDF usando regex.
    
    Args:
        text: Texto completo del PDF.
        filename: Nombre del archivo PDF.
    
    Returns:
        Dict: Metadata extraída del contrato.
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
        "requiere_confidencialidad": None,
        "nivel_seguridad": None,
        "normas": None  # STANAG, ISO, etc.
    }
    
    # Extraer número de expediente
    exp_patterns = [
        r"EXPEDIENTE:\s*([A-Z0-9_\-]+)",
        r"Expediente:\s*([A-Z0-9_\-]+)",
        r"Nº Expediente:\s*([A-Z0-9_\-]+)",
        r"([A-Z]{2,4}_\d{4}_\d{3})"
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, text)
        if match:
            metadata["num_contrato"] = match.group(1)
            break
    
    # Extraer tipo de contrato del filename o texto
    tipo_patterns = [
        r"TIPO:\s*(.+?)(?:\n|$)",
        r"CONTRATO DE\s+(\w+)",
        r"Tipo de Contrato:\s*(.+?)(?:\n|$)"
    ]
    for pattern in tipo_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["tipo_contrato"] = match.group(1).strip()
            break
    
    # Intentar extraer del nombre del archivo
    if not metadata["tipo_contrato"]:
        filename_parts = filename.replace(".pdf", "").split("_")
        if len(filename_parts) >= 4:
            metadata["tipo_contrato"] = " ".join(filename_parts[3:])
    
    # Extraer contratante
    contratante_patterns = [
        r"Contratante:\s*(.+?)(?:\n|$)",
        r"CONTRATANTE:\s*(.+?)(?:\n|$)",
        r"Órgano de Contratación:\s*(.+?)(?:\n|$)"
    ]
    for pattern in contratante_patterns:
        match = re.search(pattern, text)
        if match:
            metadata["contratante"] = match.group(1).strip()
            break
    
    # Extraer contratista
    contratista_patterns = [
        r"Contratista:\s*(.+?)(?:\n|$)",
        r"CONTRATISTA:\s*(.+?)(?:\n|$)",
        r"Adjudicatario:\s*(.+?)(?:\n|$)"
    ]
    for pattern in contratista_patterns:
        match = re.search(pattern, text)
        if match:
            metadata["contratista"] = match.group(1).strip()
            break
    
    # Extraer fechas
    fecha_inicio_patterns = [
        r"Fecha de inicio de ejecucion:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Fecha de inicio:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Inicio:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Fecha inicio:\s*(\d{1,2}/\d{1,2}/\d{4})"
    ]
    for pattern in fecha_inicio_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["fecha_inicio"] = match.group(1)
            print(f"[DEBUG] Fecha inicio encontrada: {match.group(1)}")
            break
    
    fecha_fin_patterns = [
        r"Fecha de finalizacion:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Fecha de finalización:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Fin:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Fecha fin:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Vencimiento:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Vigencia hasta el:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Finaliza el:\s*(\d{1,2}/\d{1,2}/\d{4})"
    ]
    for pattern in fecha_fin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found_date = match.group(1)
            metadata["fecha_fin"] = found_date
            print(f"[DEBUG] Fecha fin encontrada: {found_date}")
            break
    
    # Extraer importe
    importe_patterns = [
        r"Importe total:\s*([\d\.,]+)\s*(?:€|EUR)",
        r"Importe:\s*([\d\.,]+)\s*(?:€|EUR)",
        r"Precio:\s*([\d\.,]+)\s*(?:€|EUR)",
        r"([\d\.]+,\d{2})\s*(?:€|EUR)"
    ]
    for pattern in importe_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["importe"] = match.group(1) + "€"
            print(f"[DEBUG] Importe encontrado: {metadata['importe']}")
            break
            break
    
    # Extraer fecha de vencimiento del aval
    aval_fecha_patterns = [
        r"Fecha de vencimiento del aval:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Vencimiento del aval:\s*(\d{1,2}/\d{1,2}/\d{4})",
        r"Aval.*vencimiento:\s*(\d{1,2}/\d{1,2}/\d{4})",
    ]
    for pattern in aval_fecha_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["aval_vencimiento"] = match.group(1)
            print(f"[DEBUG] Aval vencimiento encontrado: {match.group(1)}")
            break
    
    # Extraer importe del aval/garantía
    aval_importe_patterns = [
        r"Garantia definitiva:\s*([\d\.,]+)\s*EUR",
        r"Garantía definitiva:\s*([\d\.,]+)\s*EUR",
        r"Importe del aval:\s*([\d\.,]+)",
    ]
    for pattern in aval_importe_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["aval_importe"] = match.group(1) + "€"
            break
    
    # Extraer entidad avalista (patrones expandidos para capturar variaciones)
    aval_entidad_patterns = [
        r"Entidad avalista:\s*(.+?)(?:\n|$)",
        r"Entidad avalista\s*:\s*(.+?)(?:\n|$)",  # Espacio antes de :
        r"Banco avalista:\s*(.+?)(?:\n|$)",
        r"Avalista:\s*(.+?)(?:\n|$)",
        r"Emitido por:\s*(.+?)(?:\n|$)",
        r"Entidad\s+avalista\s*:\s*(.+?)(?:\n|$)",  # Espacios flexibles
    ]
    for pattern in aval_entidad_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["aval_entidad"] = match.group(1).strip()
            print(f"[DEBUG] Entidad avalista encontrada: {metadata['aval_entidad']}")
            break
    
    # Extraer nivel de seguridad/confidencialidad
    seguridad_patterns = [
        r"Clasificacion de seguridad:\s*(.+?)(?:\n|$)",
        r"Clasificación de seguridad:\s*(.+?)(?:\n|$)",
        r"Nivel de seguridad:\s*(.+?)(?:\n|$)",
    ]
    for pattern in seguridad_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nivel = match.group(1).strip()
            metadata["nivel_seguridad"] = nivel
            # Si tiene clasificación diferente a "SIN CLASIFICAR", requiere confidencialidad
            if nivel and "SIN CLASIFICAR" not in nivel.upper():
                metadata["requiere_confidencialidad"] = True
            else:
                metadata["requiere_confidencialidad"] = False
            break
    
    # Extraer NORMAS Y CERTIFICACIONES (STANAG, ISO, etc.)
    normas_encontradas = []
    normas_patterns = [
        r"STANAG\s*\d+",
        r"ISO\s*\d+[:\-]?\d*",
        r"PECAL\s*\d+",
        r"AQAP[\-\s]*\d+",
        r"MIL-STD-\d+[A-Z]?",
        r"UNE-EN\s*\d+",
        r"NIJ\s+Standard[\s\d\.]+",
        r"ENS\s+Alto",
        r"NIST\s+CSF",
        r"CCN-STIC"
    ]
    for pattern in normas_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        normas_encontradas.extend(matches)
    
    if normas_encontradas:
        # Eliminar duplicados y formatear
        normas_unicas = list(set([n.upper().strip() for n in normas_encontradas]))
        metadata["normas"] = ", ".join(normas_unicas)
    
    return metadata


def split_by_sections(text: str) -> List[Dict]:
    """
    Divide el texto por secciones usando el delimitador especificado.
    
    Args:
        text: Texto completo del PDF.
    
    Returns:
        List[Dict]: Lista de secciones con nombre y contenido.
    """
    sections = []
    
    # Patrón para detectar secciones: ─── NOMBRE ───
    section_pattern = rf"{SECTION_DELIMITER}\s*(.+?)\s*{SECTION_DELIMITER}"
    
    # Encontrar todas las secciones
    matches = list(re.finditer(section_pattern, text))
    
    if not matches:
        # Si no hay secciones, tratar todo como una sección
        sections.append({
            "nombre": "Documento Completo",
            "contenido": text.strip()
        })
        return sections
    
    # Extraer contenido antes de la primera sección
    if matches[0].start() > 0:
        pre_content = text[:matches[0].start()].strip()
        if pre_content:
            sections.append({
                "nombre": "Encabezado",
                "contenido": pre_content
            })
    
    # Extraer cada sección
    for i, match in enumerate(matches):
        section_name = match.group(1).strip()
        
        # Contenido va desde el fin del match hasta el inicio del siguiente
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        
        content = text[start:end].strip()
        
        if content:
            sections.append({
                "nombre": section_name,
                "contenido": content
            })
    
    return sections


def estimate_tokens(text: str) -> int:
    """
    Estima el número de tokens en un texto.
    Aproximación: 1 token ≈ 4 caracteres en español.
    
    Args:
        text: Texto a estimar.
    
    Returns:
        int: Número estimado de tokens.
    """
    return len(text) // 4


def subdivide_large_section(section: Dict, max_tokens: int = CHUNK_MAX_TOKENS, 
                            overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """
    Subdivide una sección grande en chunks más pequeños con overlap.
    
    Args:
        section: Diccionario con nombre y contenido de la sección.
        max_tokens: Máximo de tokens por chunk.
        overlap: Tokens de overlap entre chunks.
    
    Returns:
        List[Dict]: Lista de sub-chunks.
    """
    content = section["contenido"]
    tokens = estimate_tokens(content)
    
    if tokens <= max_tokens:
        return [section]
    
    chunks = []
    max_chars = max_tokens * 4  # Aproximación
    overlap_chars = overlap * 4
    
    start = 0
    chunk_num = 1
    
    while start < len(content):
        end = start + max_chars
        
        # Intentar cortar en un punto y seguido o salto de línea
        if end < len(content):
            # Buscar el último punto o salto de línea antes del límite
            last_break = content.rfind(".", start, end)
            if last_break == -1:
                last_break = content.rfind("\n", start, end)
            if last_break > start:
                end = last_break + 1
        
        chunk_content = content[start:end].strip()
        
        if chunk_content:
            chunks.append({
                "nombre": f"{section['nombre']} (Parte {chunk_num})",
                "contenido": chunk_content
            })
            chunk_num += 1
        
        start = end - overlap_chars
        if start < 0:
            start = 0
    
    return chunks


def create_chunks_from_pdf(pdf_path: Path) -> List[Dict]:
    """
    Crea chunks enriquecidos con metadata a partir de un PDF.
    
    Args:
        pdf_path: Ruta al archivo PDF.
    
    Returns:
        List[Dict]: Lista de chunks con contenido y metadata completa.
    """
    chunks = []
    
    # Leer PDF con información de páginas
    pages_data = read_pdf_with_pages(pdf_path)
    
    if not pages_data:
        logger.warning(f"No se pudo leer el PDF: {pdf_path.name}")
        return []
    
    # Combinar texto de todas las páginas
    full_text = "\n\n".join([p["text"] for p in pages_data])
    
    # Extraer metadata global del documento
    global_metadata = extract_metadata_from_text(full_text, pdf_path.name)
    
    # Dividir por secciones
    sections = split_by_sections(full_text)
    
    # Procesar cada sección
    for section in sections:
        # Subdividir si es muy grande
        sub_sections = subdivide_large_section(section)
        
        for sub in sub_sections:
            # Determinar la página aproximada
            page_num = 1
            for page in pages_data:
                if sub["contenido"][:100] in page["text"]:
                    page_num = page["page_num"]
                    break
            
            chunk = {
                "contenido": sub["contenido"],
                "metadata": {
                    **global_metadata,
                    "seccion_pdf": sub["nombre"],
                    "pagina": page_num
                }
            }
            chunks.append(chunk)
    
    logger.info(f"Creados {len(chunks)} chunks de: {pdf_path.name}")
    return chunks


def create_chunks_from_normalized(md_path: Path) -> List[Dict]:
    """
    Crea chunks a partir de un archivo Markdown normalizado.
    Con metadata enriquecida automáticamente.
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Dividir por secciones usando el delimitador
    sections = split_by_sections(content)
    
    # El normalizador ya pone la metadata al inicio, podemos extraerla si queremos, 
    # pero para el RAG aprovecharemos que cada sección es clara.
    # Por ahora, usamos el filename para identificar el contrato original.
    original_filename = md_path.name.replace("_normalized.md", ".pdf")
    
    chunks = []
    for section in sections:
        sub_sections = subdivide_large_section(section)
        for sub in sub_sections:
            # Metadata base
            base_metadata = {
                "archivo": original_filename,
                "seccion": sub["nombre"]
            }
            
            # ENRIQUECIMIENTO AUTOMÁTICO
            enriched_metadata = enrich_chunk_metadata(
                chunk_text=sub["contenido"],
                section_name=sub["nombre"],
                base_metadata=base_metadata
            )
            
            chunks.append({
                "contenido": sub["contenido"],
                "metadata": enriched_metadata
            })
    
    logger.info(f"Creados {len(chunks)} chunks enriquecidos de: {md_path.name}")
    return chunks

def create_all_chunks() -> List[Dict]:
    """
    Crea chunks de todos los archivos NORMALIZADOS.
    """
    all_chunks = []
    md_files = list(NORMALIZED_PATH.glob("*.md"))
    
    if not md_files:
        logger.warning(f"No hay archivos normalizados en {NORMALIZED_PATH}")
        return []

    for md_path in md_files:
        chunks = create_chunks_from_normalized(md_path)
        all_chunks.extend(chunks)
    
    logger.info(f"Total: {len(all_chunks)} chunks de {len(md_files)} documentos normalizados")
    return all_chunks
