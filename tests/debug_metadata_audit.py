
import os
import sys
import logging
from pathlib import Path
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.pdf_processor import process_all_contracts
from utils.chunking import extract_metadata_from_text

def audit_metadata():
    print("\n🔍 AUDITORÍA DE METADATOS DE CONTRATOS (VERDAD DEL SISTEMA)")
    print("===========================================================\n")
    
    contracts = process_all_contracts()
    data = []
    
    for c in contracts:
        meta = extract_metadata_from_text(c["text"], c["filename"])
        data.append({
            "Archivo": c["filename"],
            "Fecha Fin (Vencimiento)": meta.get("fecha_fin", "N/A"),
            "Importe": meta.get("importe", "N/A"),
            "Avalista": meta.get("aval_entidad", "N/A"),
            "Nivel": meta.get("nivel_seguridad", "N/A")
        })
    
    # Mostrar tabla
    df = pd.DataFrame(data)
    
    # Ajustar opciones de visualización
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 50)
    
    print(df)
    
    # Análisis de fallos
    print("\n\n📊 RESUMEN DE FALLOS POTENCIALES:")
    missing_dates = df[df["Fecha Fin (Vencimiento)"] == "N/A"]
    missing_amounts = df[df["Importe"] == "N/A"]
    missing_avals = df[df["Avalista"] == "N/A"]
    
    if not missing_dates.empty:
        print(f"⚠️  FECHAS FALTANTES EN: {len(missing_dates)} contratos")
        print(missing_dates["Archivo"].tolist())
    else:
        print("✅  Todas las FECHAS detectadas.")
        
    if not missing_amounts.empty:
        print(f"⚠️  IMPORTES FALTANTES EN: {len(missing_amounts)} contratos")
        print(missing_amounts["Archivo"].tolist())
    else:
        print("✅  Todos los IMPORTES detectados.")

    if not missing_avals.empty:
        print(f"⚠️  AVALISTAS FALTANTES EN: {len(missing_avals)} contratos")
        print(missing_avals["Archivo"].tolist())
    else:
        print("✅  Todos los AVALISTAS detectados.")
        
if __name__ == "__main__":
    audit_metadata()
