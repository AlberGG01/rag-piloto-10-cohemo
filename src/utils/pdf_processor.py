# -*- coding: utf-8 -*-
"""
Procesamiento de archivos PDF.
Lee y extrae texto de contratos PDF.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict

import pdfplumber

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import CONTRACTS_PATH

logger = logging.getLogger(__name__)


def read_pdf(pdf_path: Path) -> Optional[str]:
    """
    Lee un archivo PDF y extrae todo su texto.
    
    Args:
        pdf_path: Ruta al archivo PDF.
    
    Returns:
        str: Texto extraído del PDF o None si hay error.
    """
    try:
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        full_text = "\n\n".join(text_parts)
        logger.info(f"PDF leído correctamente: {pdf_path.name} ({len(full_text)} caracteres)")
        return full_text
        
    except Exception as e:
        logger.error(f"Error leyendo PDF {pdf_path.name}: {e}")
        return None


def read_pdf_with_pages(pdf_path: Path) -> List[Dict]:
    """
    Lee un PDF y retorna texto por página con metadata.
    
    Args:
        pdf_path: Ruta al archivo PDF.
    
    Returns:
        List[Dict]: Lista de diccionarios con texto y número de página.
    """
    pages_data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    pages_data.append({
                        "page_num": page_num,
                        "text": page_text,
                        "filename": pdf_path.name
                    })
        
        logger.info(f"PDF leído con {len(pages_data)} páginas: {pdf_path.name}")
        
    except Exception as e:
        logger.error(f"Error leyendo PDF con páginas {pdf_path.name}: {e}")
    
    return pages_data


def get_all_contracts() -> List[Path]:
    """
    Obtiene todos los archivos PDF de la carpeta de contratos.
    
    Returns:
        List[Path]: Lista de rutas a archivos PDF.
    """
    contracts_path = Path(CONTRACTS_PATH)
    
    if not contracts_path.exists():
        logger.warning(f"La carpeta de contratos no existe: {contracts_path}")
        contracts_path.mkdir(parents=True, exist_ok=True)
        return []
    
    pdf_files = list(contracts_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"No se encontraron PDFs en: {contracts_path}")
    else:
        logger.info(f"Encontrados {len(pdf_files)} contratos PDF")
    
    return sorted(pdf_files)


def get_contracts_count() -> int:
    """
    Cuenta el número de contratos PDF disponibles.
    
    Returns:
        int: Número de archivos PDF.
    """
    return len(get_all_contracts())


def process_all_contracts() -> List[Dict]:
    """
    Procesa todos los contratos y retorna sus datos.
    
    Returns:
        List[Dict]: Lista con nombre de archivo y texto de cada contrato.
    """
    contracts = []
    pdf_files = get_all_contracts()
    
    for pdf_path in pdf_files:
        text = read_pdf(pdf_path)
        
        if text:
            contracts.append({
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "text": text
            })
        else:
            logger.warning(f"No se pudo extraer texto de: {pdf_path.name}")
    
    logger.info(f"Procesados {len(contracts)} de {len(pdf_files)} contratos")
    return contracts
