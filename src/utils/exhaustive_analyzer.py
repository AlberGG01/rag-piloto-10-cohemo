# -*- coding: utf-8 -*-
"""
Módulo de análisis exhaustivo de datos multi-documentos.
Fase 2 P3: Extracción masiva de fechas/importes por contrato para queries comparativas.
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime
from src.utils.deterministic_extractor import extract_dates, extract_amounts


def extract_all_dates_by_contract(chunks: List[Dict]) -> Dict[str, List[str]]:
    """
    Extrae TODAS las fechas de TODOS los chunks, agrupadas por contrato.
    
    Args:
        chunks: Lista de chunks devueltos por hybrid_search
    
    Returns:
        Dict[contract_id, List[fechas]] - Fechas deduplicadas por contrato
    """
    contract_dates = {}
    
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        contract_id = metadata.get("num_contrato", "UNKNOWN")
        content = chunk.get("contenido", "")
        
        # Extraer fechas del contenido
        dates = extract_dates(content)
        
        if contract_id not in contract_dates:
            contract_dates[contract_id] = set()
        
        contract_dates[contract_id].update(dates)
    
    # Convertir sets a listas ordenadas
    result = {}
    for contract_id, dates_set in contract_dates.items():
        result[contract_id] = sorted(list(dates_set), key=lambda d: parse_date_to_comparable(d))
    
    return result


def parse_date_to_comparable(date_str: str) -> Tuple[int, int, int]:
    """
    Convierte fecha DD/MM/AAAA a tupla (AAAA, MM, DD) para comparación.
    """
    try:
        day, month, year = map(int, date_str.split('/'))
        return (year, month, day)
    except:
        return (9999, 12, 31)  # Fecha inválida al final


def find_contracts_with_date(target_date: str, contract_dates: Dict[str, List[str]]) -> List[str]:
    """
    Encuentra contratos que contengan una fecha específica.
    
    Args:
        target_date: Fecha a buscar (formato DD/MM/AAAA)
        contract_dates: Dict de fechas por contrato
    
    Returns:
        Lista de contract_ids que contienen la fecha
    """
    matches = []
    
    for contract_id, dates in contract_dates.items():
        if target_date in dates:
            matches.append(contract_id)
    
    return matches


def find_contract_with_most_dates(contract_dates: Dict[str, List[str]]) -> Tuple[str, int]:
    """
    Encuentra el contrato con mayor densidad de hitos (más fechas).
    
    Returns:
        (contract_id, número_de_fechas)
    """
    max_dates = 0
    winner = None
    
    for contract_id, dates in contract_dates.items():
        if len(dates) > max_dates:
            max_dates = len(dates)
            winner = contract_id
    
    return winner, max_dates


def extract_all_amounts_by_contract(chunks: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Extrae TODOS los importes de TODOS los chunks, agrupados por contrato.
    
    Args:
        chunks: Lista de chunks devueltos por hybrid_search
    
    Returns:
        Dict[contract_id, List[{valor, contexto}]] - Importes por contrato
    """
    contract_amounts = {}
    
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        contract_id = metadata.get("num_contrato", "UNKNOWN")
        content = chunk.get("contenido", "")
        
        # Extraer importes
        amounts = extract_amounts(content)
        
        if contract_id not in contract_amounts:
            contract_amounts[contract_id] = []
        
        contract_amounts[contract_id].extend(amounts)
    
    # Deduplicar importes por valor
    result = {}
    for contract_id, amounts_list in contract_amounts.items():
        seen_values = set()
        unique_amounts = []
        
        for amount_dict in amounts_list:
            value = amount_dict["valor"]
            if value not in seen_values:
                seen_values.add(value)
                unique_amounts.append(amount_dict)
        
        result[contract_id] = unique_amounts
    
    return result


def find_contract_with_min_amount(contract_amounts: Dict[str, List[Dict]]) -> Tuple[str, str]:
    """
    Encuentra el contrato con menor importe total.
    
    Returns:
        (contract_id, importe_menor_formateado)
    """
    min_amount = float('inf')
    winner = None
    winner_formatted = None
    
    for contract_id, amounts_list in contract_amounts.items():
        if not amounts_list:
            continue
        
        # Asumir que el primer importe es el importe total del contrato
        # (normalmente aparece primero en el documento)
        first_amount = amounts_list[0]["valor"]
        
        # Convertir a float para comparación (X.XXX.XXX,XX -> XXXXXXX.XX)
        amount_float = parse_amount_to_float(first_amount)
        
        if amount_float < min_amount:
            min_amount = amount_float
            winner = contract_id
            winner_formatted = first_amount
    
    return winner, winner_formatted


def find_contract_with_max_amount(contract_amounts: Dict[str, List[Dict]]) -> Tuple[str, str]:
    """
    Encuentra el contrato con mayor importe total.
    
    Returns:
        (contract_id, importe_mayor_formateado)
    """
    max_amount = 0
    winner = None
    winner_formatted = None
    
    for contract_id, amounts_list in contract_amounts.items():
        if not amounts_list:
            continue
        
        first_amount = amounts_list[0]["valor"]
        amount_float = parse_amount_to_float(first_amount)
        
        if amount_float > max_amount:
            max_amount = amount_float
            winner = contract_id
            winner_formatted = first_amount
    
    return winner, winner_formatted


def parse_amount_to_float(amount_str: str) -> float:
    """
    Convierte importe español a float.
    Ej: "28.500.000,00" -> 28500000.00
    """
    try:
        # Quitar puntos de miles y reemplazar coma por punto
        cleaned = amount_str.replace(".", "").replace(",", ".")
        return float(cleaned)
    except:
        return 0.0


def analyze_query_criteria(query: str) -> Dict:
    """
    Detecta queries con múltiples criterios AND.
    Fase 2 P1: Query Analyzer para multi-criterio.
    
    Ej: "ISO Y STANAG" → {"type": "MULTI_CRITERIA", "criteria": ["ISO", "STANAG"]}
    """
    and_keywords = [" y ", " e ", " con ", " que tenga", " combina", " combine"]
    normativas_pattern = r'\b(ISO|STANAG|MIL-\w+|UNE-EN)\b'
    
    query_lower = query.lower()
    
    # Detectar AND lógico
    has_and = any(kw in query_lower for kw in and_keywords)
    
    if has_and:
        # Extraer normativas mencionadas
        normativas = list(set(re.findall(normativas_pattern, query, re.IGNORECASE)))
        
        if len(normativas) >= 2:
            return {
                "type": "MULTI_CRITERIA",
                "criteria": normativas,
                "description": f"AND lógico: {' + '.join(normativas)}"
            }
    
    return {"type": "SINGLE"}


def filter_chunks_by_all_criteria(chunks: List[Dict], criteria: List[str]) -> List[Dict]:
    """
    Post-filtra chunks para que contengan TODOS los criterios (AND lógico).
    
    Args:
        chunks: Chunks originales
        criteria: Lista de normativas/keywords que DEBEN estar presentes
    
    Returns:
        Chunks filtrados que contienen todos los criterios
    """
    filtered = []
    
    for chunk in chunks:
        content = chunk.get("contenido", "").upper()
        metadata = chunk.get("metadata", {})
        
        # Verificar que TODOS los criterios estén presentes
        all_present = all(criterion.upper() in content for criterion in criteria)
        
        if all_present:
            # Añadir score boost por multi-criterio
            if "final_score" in metadata:
                metadata["final_score"] += 2.0  # Boost significativo
            
            filtered.append(chunk)
    
    return filtered
