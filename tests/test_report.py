# -*- coding: utf-8 -*-
"""Test script to debug report generation."""

import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.pdf_processor import process_all_contracts
from src.utils.chunking import extract_metadata_from_text
from src.agents.analyzer_agent import analyze_all_contracts
from src.agents.report_agent import create_alerts_dataframe

print("=" * 60)
print("TEST DE GENERACIÓN DE INFORMES")
print("=" * 60)

# 1. Obtener contratos
print("\n1. Leyendo contratos PDF...")
contracts = process_all_contracts()
print(f"   Contratos encontrados: {len(contracts)}")

if not contracts:
    print("   ERROR: No hay contratos para procesar")
    sys.exit(1)

# 2. Extraer metadata y mostrar fechas
print("\n2. Extrayendo metadata de contratos...")
extracted_data = []
for contract in contracts:
    print(f"\n   Procesando: {contract['filename']}")
    metadata = extract_metadata_from_text(contract["text"], contract["filename"])
    
    # Mostrar fechas encontradas
    print(f"      - Fecha inicio: {metadata.get('fecha_inicio')}")
    print(f"      - Fecha fin: {metadata.get('fecha_fin')}")
    print(f"      - Num contrato: {metadata.get('num_contrato')}")
    print(f"      - Aval vencimiento: {metadata.get('aval_vencimiento')}")
    print(f"      - Aval importe: {metadata.get('aval_importe')}")
    print(f"      - Confidencialidad: {metadata.get('requiere_confidencialidad')}")
    
    # Convertir a formato del analizador
    data = {
        "num_expediente": metadata.get("num_contrato"),
        "tipo_contrato": metadata.get("tipo_contrato"),
        "contratante": metadata.get("contratante"),
        "contratista": metadata.get("contratista"),
        "fecha_inicio": metadata.get("fecha_inicio"),
        "fecha_fin": metadata.get("fecha_fin"),
        "importe_total": metadata.get("importe"),
        "_archivo": contract["filename"],
        "aval_vencimiento": metadata.get("aval_vencimiento"),
        "aval_importe": metadata.get("aval_importe"),
        "aval_entidad": metadata.get("aval_entidad"),
        "permite_revision_precios": None,
        "requiere_confidencialidad": metadata.get("requiere_confidencialidad"),
        "hitos_entrega": []
    }
    extracted_data.append(data)

# 3. Analizar alertas
print("\n3. Analizando alertas...")
alerts = analyze_all_contracts(extracted_data)
print(f"   Alertas generadas: {len(alerts)}")

if alerts:
    print("\n   ALERTAS ENCONTRADAS:")
    for i, alert in enumerate(alerts[:10], 1):
        print(f"   {i}. {alert.get('expediente')}: {alert.get('observacion')[:50]}... [{alert.get('prioridad')}]")
else:
    print("   NO SE GENERARON ALERTAS")

# 4. Crear DataFrame
print("\n4. Creando DataFrame...")
df = create_alerts_dataframe(alerts)
print(f"   Filas en DataFrame: {len(df)}")
if not df.empty:
    print("\n   TABLA:")
    print(df.to_string())

print("\n" + "=" * 60)
print("TEST COMPLETADO")
print("=" * 60)
