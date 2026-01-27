# -*- coding: utf-8 -*-
"""
Data Safety Utils - Cinturón de Seguridad Numérico (v4.2).
Valida que la reparación de texto no haya alterado las cifras.
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def extract_numeric_footprint(text: str) -> List[str]:
    """
    Extrae todos los números del texto en orden de aparición.
    Normaliza formatos (elimina separadores de miles, etc) para comparación robusta.
    
    Args:
        text: Texto a analizar.
        
    Returns:
        List[str]: Lista de secuencias numéricas encontradas.
    """
    # Regex para capturar números:
    # Captura enteros y decimales. Ignora fechas si es posible, pero para footprint estricta
    # capturamos TODO lo que parezca un número significativo.
    # Patrón busca dígitos conectados por puntos o comas.
    
    # Estrategia: Encontrar secuencias de dígitos que pueden tener . o , intercalados
    matches = re.findall(r'\d+(?:[.,]\d+)*', text)
    
    # Normalización: '1.500,00' -> '1500,00' -> '1500.00' (float standard)?
    # O mejor, limpieza simple: quitar '.' (miles) y dejar ',' como decimal?
    # Problema: 1.500 (mil quinientos) vs 1.5 (uno punto cinco).
    # SOLUCIÓN ROBUSTA PARA COMPARACIÓN DIRECTA:
    # No interpretamos el valor, solo comparamos la SECUENCIA de dígitos significativa.
    # Si el original es "1.500" y el reparado es "1,500", asumimos equivalencia si el contexto es ES/EN.
    # PERO para "Strict Mode", la reparación NO debe cambiar ni una coma.
    # Entonces devolvemos la lista RAW.
    
    return matches

def compare_numeric_footprint(original: str, repaired: str) -> Tuple[bool, str]:
    """
    Compara la huella numérica de dos textos.
    
    Args:
        original: Texto original (roto).
        repaired: Texto reparado.
        
    Returns:
        (CheckPassed, Reason)
    """
    nums_orig = extract_numeric_footprint(original)
    nums_rep = extract_numeric_footprint(repaired)
    
    if len(nums_orig) != len(nums_rep):
        # Fallo de cantidad
        missing = len(nums_orig) - len(nums_rep)
        return False, f"Cantidad de números no coincide. Original: {len(nums_orig)}, Reparado: {len(nums_rep)}. Delta: {missing}"
    
    # Comparación elemento a elemento
    errors = []
    for i, (n_orig, n_rep) in enumerate(zip(nums_orig, nums_rep)):
        if n_orig != n_rep:
            # Intento de normalización flexible (ej: cambio de punto por coma)
            # Si el usuario permite flexibilidad, bien. Si es STRICT MODE, fallo.
            # El prompt pedía: "El orden y el valor de cada número deben ser idénticos."
            # Asumimos identidad estricta de caracteres para máxima seguridad.
            errors.append(f"Pos {i}: '{n_orig}' != '{n_rep}'")
            
    if errors:
        return False, f"Discrepancia numérica detectada: {'; '.join(errors[:3])}..."
        
    return True, "OK"
