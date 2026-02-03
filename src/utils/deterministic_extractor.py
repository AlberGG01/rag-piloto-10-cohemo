# -*- coding: utf-8 -*-
"""
Módulo de extracción determinista de datos específicos.
Utiliza regex para extraer CIFs, fechas, importes y normativas de forma precisa.
"""

import re
from typing import Dict, Optional, List


def extract_cif(text: str) -> Optional[str]:
    """
    Extrae CIF/NIF español del texto.
    Formato: [A-Z]-XXXXXXXX o [A-Z]XXXXXXXX
    """
    pattern = r'\b([A-Z])-?(\d{8})\b'
    match = re.search(pattern, text)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return None


def extract_cifs(text: str) -> List[str]:
    """
    Extrae TODOS los CIFs encontrados en el texto.
    """
    pattern = r'\b([A-Z])-?(\d{8})\b'
    matches = re.finditer(pattern, text)
    
    cifs = []
    for match in matches:
        cifs.append(f"{match.group(1)}-{match.group(2)}")
    
    return list(set(cifs))


def extract_dates(text: str) -> List[str]:
    """
    Extrae todas las fechas en formato DD/MM/AAAA.
    """
    pattern = r'\b(\d{2}/\d{2}/\d{4})\b'
    matches = re.findall(pattern, text)
    return matches


def extract_amounts(text: str) -> List[Dict[str, str]]:
    """
    Extrae importes en formato español: X.XXX.XXX,XX EUR
    Retorna lista de {valor, contexto}
    """
    # Patrón para importes con céntimos
    pattern = r'(\d{1,3}(?:\.\d{3})*,\d{2})\s?EUR'
    matches = re.finditer(pattern, text)
    
    results = []
    for match in matches:
        amount = match.group(1)
        # Extraer contexto (50 chars antes y después)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].strip()
        results.append({"valor": amount, "contexto": context})
    
    return results


def extract_normativas(text: str) -> List[str]:
    """
    Extrae normativas militares y civiles.
    Formatos: ISO XXXXX, STANAG XXXX, MIL-XXX-XXXX, UNE-EN ISO XXXXX
    """
    patterns = [
        r'\bISO[\s-]?\d+(?::\d{4})?\b',  # ISO 9001, ISO 9001:2015
        r'\bSTANAG[\s-]?\d+\b',           # STANAG 4172
        r'\bMIL-[A-Z]{3}-\d+\b',          # MIL-DTL-83133
        r'\bUNE-EN[\s-]?ISO[\s-]?\d+\b', # UNE-EN ISO 18788
        r'\bDirectiva\s+\d+/\d+/[A-Z]+\b', # Directiva 93/42/CEE
        r'\bReglamento[\s(]+CE[\s)]+\d+/\d{4}\b'  # Reglamento CE 852/2004
    ]
    
    normativas = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        normativas.extend(matches)
    
    # Deduplicar y normalizar
    return list(set([n.strip() for n in normativas]))


def extract_penalties(text: str) -> List[Dict[str, str]]:
    """
    Extrae penalizaciones específicas.
    Formatos:
    - X.XXX,XX EUR por día
    - X% del importe por día
    - XX.XXX EUR diarios
    """
    patterns = [
        # Penalización fija (50.000 EUR diarios, 10.000 EUR por día)
        r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s?EUR\s+(?:diarios?|por\s+día)',
        # Penalización porcentual (0,5% del importe por día)
        r'(\d+,?\d*)\s?%\s+del\s+importe\s+por\s+(?:día|semana)',
    ]
    
    penalties = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Contexto
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            context = text[start:end].strip()
            penalties.append({
                "valor": match.group(1),
                "contexto": context,
                "tipo": "fija" if "EUR" in match.group(0) else "porcentual"
            })
    
    return penalties


def extract_contract_id(text: str) -> Optional[str]:
    """
    Extrae ID de contrato mencionado en query.
    Formato: CON_2024_012, SER_2024_015, etc.
    """
    pattern = r'\b(CON|SER|SUM|LIC)_\d{4}_\d{3}\b'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return None


def extract_contract_ids(text: str) -> List[str]:
    """
    Extrae TODOS los IDs de contrato mencionados.
    """
    pattern = r'\b(CON|SER|SUM|LIC)_\d{4}_\d{3}\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # re.findall con grupos retorna tuplas si hay grupos, pero aqui el grupo es (CON|SER...)
    # Mejor usar finditer para consistencia o ajustar regex
    # Ajustando regex para capturar todo
    pattern_full = r'\b(?:CON|SER|SUM|LIC)_\d{4}_\d{3}\b'
    matches = re.findall(pattern_full, text, re.IGNORECASE)
    
    return list(set([m.upper() for m in matches]))


def is_generic_iso_9001(text: str) -> bool:
    """
    Detecta si menciona ISO 9001 SIN especificar año.
    True si encuentra "ISO 9001" pero NO "ISO 9001:20XX"
    """
    # Buscar ISO 9001 con año
    if re.search(r'ISO[\s-]?9001:\d{4}', text, re.IGNORECASE):
        return False
    
    # Buscar ISO 9001 genérica
    if re.search(r'ISO[\s-]?9001\b(?!:)', text, re.IGNORECASE):
        return True
    
    return False


def contains_exact_amount(text: str, target_amount: str) -> bool:
    """
    Verifica si el texto contiene el importe exacto especificado.
    Útil para queries como "penalización de 50.000 EUR".
    """
    # Normalizar el importe objetivo (quitar puntos)
    target_normalized = target_amount.replace(".", "").replace(",", ".")
    
    # Buscar en el texto
    amounts = extract_amounts(text)
    for amount_dict in amounts:
        amount_normalized = amount_dict["valor"].replace(".", "").replace(",", ".")
        if amount_normalized == target_normalized:
            return True
    
    return False


def extract_final_execution_date(text: str) -> Optional[str]:
    """
    Extrae la fecha final de ejecución material.
    Busca keywords: "finalización", "ejecución final", "término"
    """
    # Buscar contexto de finalización
    patterns = [
        r'(?:fecha\s+final|finalización|término|conclusión).*?(\d{2}/\d{2}/\d{4})',
        r'(\d{2}/\d{2}/\d{4}).*?(?:fecha\s+final|finalización|término)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1)
    
    # Si no encuentra, retornar la fecha más tardía del documento
    all_dates = extract_dates(text)
    if all_dates:
        # Convertir a formato comparable y retornar la más tardía
        dates_parsed = []
        for date_str in all_dates:
            try:
                day, month, year = map(int, date_str.split('/'))
                dates_parsed.append((year, month, day, date_str))
            except:
                continue
        
        if dates_parsed:
            dates_parsed.sort(reverse=True)
            return dates_parsed[0][3]
    
    return None
