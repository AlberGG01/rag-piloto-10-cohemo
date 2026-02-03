# -*- coding: utf-8 -*-
"""
Procesamiento de archivos PDF con PyMuPDF (LangChain).
Mejor extracción de texto y metadatos estructurales.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import CONTRACTS_PATH

logger = logging.getLogger(__name__)


def load_pdf_documents(pdf_path: Path) -> List[Document]:
    """
    Carga un PDF usando PyMuPDFLoader.
    Preserva mejor la estructura y tablas que pdfplumber.
    
    Args:
        pdf_path: Ruta al archivo PDF.
    
    Returns:
        List[Document]: Lista de documentos LangChain (uno por página).
    """
    try:
        loader = PyMuPDFLoader(str(pdf_path))
        documents = loader.load()
        
        # Enriquecer metadatos
        for doc in documents:
            doc.metadata["filename"] = pdf_path.name
            doc.metadata["path"] = str(pdf_path)
            
            # Normalizar número de página (PyMuPDF usa 0-indexed a veces, aseguramos 1-indexed)
            if "page" in doc.metadata:
                 doc.metadata["page"] = doc.metadata["page"] + 1
            elif "page_number" in doc.metadata:
                 doc.metadata["page"] = doc.metadata["page_number"] + 1
            else:
                 doc.metadata["page"] = 1 # Fallback
                 
        logger.info(f"PDF cargado: {pdf_path.name} ({len(documents)} páginas)")
        return documents
        
    except Exception as e:
        logger.error(f"Error cargando PDF {pdf_path.name}: {e}")
        return []


def get_all_contracts(use_normalized: bool = True) -> List[Path]:
    """
    Obtiene todos los archivos de contratos.
    
    Args:
        use_normalized: Si True, usa archivos .md normalizados.
                       Si False, usa PDFs originales.
    
    Returns:
        Lista de rutas a archivos de contratos
    """
    if use_normalized:
        # Usar archivos normalizados (.md)
        from src.config import NORMALIZED_PATH
        contracts_path = Path(NORMALIZED_PATH)
        extension = "*.md"
    else:
        # Usar PDFs originales
        contracts_path = Path(CONTRACTS_PATH)
        extension = "*.pdf"
    
    if not contracts_path.exists():
        logger.warning(f"La carpeta de contratos no existe: {contracts_path}")
        contracts_path.mkdir(parents=True, exist_ok=True)
        return []
    
    files = list(contracts_path.glob(extension))
    logger.info(f"📂 Encontrados {len(files)} archivos en {contracts_path}")
    return sorted(files)


def process_contract_for_ingestion(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Procesa un contrato y devuelve una lista de chunks diccionarios 
    listos para ser usados por el splitter.
    """
    documents = load_pdf_documents(pdf_path)
    processed_data = []
    
    for doc in documents:
        processed_data.append({
            "text": doc.page_content,
            "metadata": doc.metadata
        })
        
    return processed_data
