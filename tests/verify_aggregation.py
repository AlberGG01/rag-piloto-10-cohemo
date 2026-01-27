# -*- coding: utf-8 -*-
"""
Script de Verificación para Agregación y Diversidad.
Prueba la query SYN_03 que fallaba anteriormente.
"""

import sys
import os
from pathlib import Path
import logging

# Añadir raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configurar logging para ver la traza del Planner
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from src.agents.rag_agent import retrieve_and_generate

def verify_fix():
    query = "Suma los importes totales (IVA incluido) de los contratos adjudicados a 'CyberDefense Iberia' y 'Thales Espana'."
    
    print(f"\n--- VERIFICANDO QUERY: {query} ---\n")
    
    result = retrieve_and_generate(query)
    
    response = result.get("response", "")
    sources = result.get("sources", [])
    
    print("\n--- RESPUESTA GENERADA ---\n")
    print(response)
    
    print("\n--- FUENTES RECUPERADAS ---\n")
    for s in sources:
        print(f"- {s.get('contrato')} | {s.get('seccion')}")
        
    # Verificar si están ambos contratos
    # Thales -> CON_2024_016 (Vision Nocturna) -> 4.2M
    # CyberDefense -> CON_2024_004 (Ciberseguridad) -> 4.5M
    # Suma: 8.7M
    
    has_thales = any("CON_2024_016" in s.get("contrato", "") for s in sources)
    has_cyber = any("CON_2024_004" in s.get("contrato", "") for s in sources)
    
    if has_thales and has_cyber:
        print("\n✅ ÉXITO: Se recuperaron fragmentos de ambos contratos.")
    else:
        print("\n❌ FALLO: Faltan contratos en el contexto.")
        print(f"   - Tiene Thales? {has_thales}")
        print(f"   - Tiene CyberDefense? {has_cyber}")

if __name__ == "__main__":
    verify_fix()
