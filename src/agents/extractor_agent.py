# -*- coding: utf-8 -*-
"""
Agente Extractor: Lee PDFs y extrae datos estructurados usando el LLM.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import EXTRACTION_PROMPT
from src.utils.pdf_processor import process_all_contracts
from src.utils.llm_config import generate_response, is_model_available

logger = logging.getLogger(__name__)


def clean_json_response(response: str) -> str:
    """
    Limpia la respuesta del LLM para obtener JSON válido.
    
    Args:
        response: Respuesta cruda del LLM.
    
    Returns:
        str: JSON limpio.
    """
    # Eliminar bloques de código markdown
    response = response.strip()
    
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]
    
    # Encontrar el JSON válido
    start = response.find("{")
    end = response.rfind("}") + 1
    
    if start != -1 and end > start:
        response = response[start:end]
    
    return response.strip()


def extract_contract_data(contract_text: str, filename: str) -> Optional[Dict]:
    """
    Extrae datos estructurados de un contrato usando el LLM.
    
    Args:
        contract_text: Texto completo del contrato.
        filename: Nombre del archivo para logging.
    
    Returns:
        Dict: Datos extraídos o None si hay error.
    """
    if not is_model_available():
        logger.error("Modelo no disponible")
        return None
    
    try:
        # Preparar prompt
        prompt = EXTRACTION_PROMPT.format(contenido=contract_text[:8000])  # Limitar contexto
        
        # Generar respuesta
        response = generate_response(prompt, max_tokens=2000, temperature=0.1)
        
        # Limpiar y parsear JSON
        clean_response = clean_json_response(response)
        
        try:
            data = json.loads(clean_response)
            data["_archivo"] = filename  # Añadir referencia al archivo
            logger.info(f"Datos extraídos de: {filename}")
            return data
            
        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando JSON de {filename}: {e}")
            logger.debug(f"Respuesta recibida: {clean_response[:500]}")
            return None
            
    except Exception as e:
        logger.error(f"Error extrayendo datos de {filename}: {e}")
        return None


def extract_all_contracts() -> List[Dict]:
    """
    Extrae datos de todos los contratos disponibles.
    
    Returns:
        List[Dict]: Lista de datos extraídos de cada contrato.
    """
    contracts = process_all_contracts()
    
    if not contracts:
        logger.warning("No hay contratos para procesar")
        return []
    
    extracted_data = []
    
    for contract in contracts:
        data = extract_contract_data(
            contract_text=contract["text"],
            filename=contract["filename"]
        )
        
        if data:
            extracted_data.append(data)
        else:
            # Crear entrada con datos mínimos si falla la extracción
            extracted_data.append({
                "_archivo": contract["filename"],
                "num_expediente": contract["filename"].replace(".pdf", ""),
                "_error": "No se pudo extraer datos con el LLM"
            })
    
    logger.info(f"Extraídos datos de {len(extracted_data)} contratos")
    return extracted_data


def run_extractor_node(state: Dict) -> Dict:
    """
    Nodo del grafo LangGraph: Ejecuta la extracción de datos.
    
    Args:
        state: Estado actual del grafo.
    
    Returns:
        Dict: Estado actualizado con datos extraídos.
    """
    logger.info("=== AGENTE EXTRACTOR: Iniciando extracción ===")
    
    extracted_data = extract_all_contracts()
    
    return {
        **state,
        "extracted_data": extracted_data,
        "extraction_complete": True,
        "contracts_count": len(extracted_data)
    }
