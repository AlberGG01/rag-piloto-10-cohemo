# -*- coding: utf-8 -*-
"""
Metadata Patch Script
---------------------
Lee los archivos Markdown normalizados, extrae el campo 'Contratista' o 'Adjudicatario',
y actualiza la metadata de los chunks correspondientes en ChromaDB.
"""

import sys
import os
from pathlib import Path
import re
import logging

# Añadir raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.vectorstore import get_collection
from src.config import NORMALIZED_PATH

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_adjudicatario(md_path: Path) -> str:
    """Extrae el nombre del adjudicatario del contenido Markdown."""
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Patrones posibles
        patterns = [
            r"- Contratista:\s*(.+?)(?:\n|$)",
            r"- Adjudicatario:\s*(.+?)(?:\n|$)",
            r"Adjudicatario:\s*(.+?)(?:\n|$)",
            r"Contratista:\s*(.+?)(?:\n|$)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                clean_name = match.group(1).strip().strip('*').strip()
                return clean_name
                
        return None
    except Exception as e:
        logger.error(f"Error leyendo {md_path}: {e}")
        return None

def patch_chromadb():
    """Actualiza ChromaDB con el campo 'adjudicatario'."""
    collection = get_collection()
    if not collection:
        logger.error("No se pudo conectar a ChromaDB")
        return

    # Obtener archivos normalizados
    md_files = list(NORMALIZED_PATH.glob("*.md"))
    logger.info(f"Encontrados {len(md_files)} archivos para procesar")

    updated_count = 0
    
    for md_file in md_files:
        adjudicatario = extract_adjudicatario(md_file)
        if not adjudicatario:
            logger.warning(f"No se encontró adjudicatario en {md_file.name}")
            continue
            
        logger.info(f"Procesando {md_file.name} -> Adjudicatario: {adjudicatario}")
        
        # El nombre del archivo en metadata suele ser el PDF original
        # Asumimos que el .md se llama igual que el .pdf + _normalized.md o similar
        # En chunking.py: original_filename = md_path.name.replace("_normalized.md", ".pdf")
        original_pdf_name = md_file.name.replace("_normalized.md", ".pdf")
        
        # Buscar chunks de este archivo
        # Chroma 'where' filter
        results = collection.get(
            where={"archivo": original_pdf_name}
        )
        
        chunk_ids = results['ids']
        metadatas = results['metadatas']
        
        if not chunk_ids:
            logger.warning(f"  No se encontraron chunks para {original_pdf_name} en Chroma")
            # Intento alternativo sin extensión si falló
            original_pdf_name_simple = md_file.name.replace("_normalized.md", "")
            results = collection.get(where={"archivo": original_pdf_name_simple})
            chunk_ids = results['ids']
            metadatas = results['metadatas']
            if not chunk_ids:
                logger.warning("  Tampoco se encontraron chunks con nombre simple")
                continue

        # Preparar actualizaciones
        new_metadatas = []
        for meta in metadatas:
            # Añadir o actualizar campo adjudicatario
            # Asegurar que todos los valores son strings/bools/ints para Chroma
            meta['adjudicatario'] = adjudicatario
            # También normalizar 'contratista' si existe/no existe para consistencia
            meta['contratista'] = adjudicatario 
            new_metadatas.append(meta)
            
        # Update en batch
        try:
            collection.update(
                ids=chunk_ids,
                metadatas=new_metadatas
            )
            updated_count += len(chunk_ids)
            logger.info(f"  Actualizados {len(chunk_ids)} chunks")
        except Exception as e:
            logger.error(f"  Error actualizando chunks: {e}")

    logger.info(f"PATCH FINALIZADO. Total chunks actualizados: {updated_count}")

if __name__ == "__main__":
    patch_chromadb()
