# -*- coding: utf-8 -*-
"""
Reporting Workflow - Lógica para el análisis masivo y generación de reportes.
Separado del flujo conversacional (Agentic RAG) para eficiencia en el Dashboard.
"""

import logging
from typing import Dict, List
from pathlib import Path

from src.config import NORMALIZED_PATH
from src.utils.chunking import extract_metadata_from_text
from src.agents.analyzer_agent import analyze_all_contracts
from src.agents.report_agent import create_alerts_dataframe, generate_excel_report

logger = logging.getLogger(__name__)

def run_quick_analysis() -> Dict:
    """
    Ejecuta un análisis rápido de todos los contratos disponibles.
    
    1. Lee todos los archivos normalizados (Markdown).
    2. Extrae metadatos (fechas, importes) usando Regex.
    3. Analiza reglas de negocio (Alertas).
    4. Genera DataFrame y Excel.
    
    Returns:
        Dict: Resultado con {success, dataframe, excel_path, alerts_summary}
    """
    try:
        logger.info("Iniciando análisis rápido (Quick Analysis)...")
        
        # 1. Recolectar datos de todos los contratos
        md_files = list(NORMALIZED_PATH.glob("*.md"))
        if not md_files:
            return {
                "success": False,
                "error": "No hay contratos normalizados. Ejecuta 'python normalize_all.py' primero."
            }
        
        extracted_data = []
        for md_path in md_files:
            try:
                content = md_path.read_text(encoding="utf-8")
                # Usar el nombre del PDF original como referencia
                original_name = md_path.name.replace("_normalized.md", ".pdf")
                
                # Extraer metadata con Regex (muy rápido)
                meta = extract_metadata_from_text(content, original_name)
                
                # Añadir campo auxiliar para el analizador
                meta["_archivo"] = original_name
                
                extracted_data.append(meta)
            except Exception as e:
                logger.error(f"Error procesando {md_path.name}: {e}")
                
        logger.info(f"Metadatos extraídos de {len(extracted_data)} contratos.")
        
        # 2. Ejecutar Analizador (Lógica de Negocio)
        alerts = analyze_all_contracts(extracted_data)
        
        # 3. Calcular resumen
        high_count = sum(1 for a in alerts if "🔴" in a["prioridad"])
        medium_count = sum(1 for a in alerts if "🟡" in a["prioridad"])
        low_count = sum(1 for a in alerts if "🟢" in a["prioridad"])
        
        alerts_summary = {
            "total": len(alerts),
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        }
        
        # 4. Generar Reportes (Report Agent Logic)
        df = create_alerts_dataframe(alerts)
        excel_path, success = generate_excel_report(df, alerts_summary)
        
        return {
            "success": True,
            "dataframe": df,
            "excel_path": excel_path,
            "alerts_summary": alerts_summary,
            "alerts": alerts
        }

    except Exception as e:
        logger.error(f"Fallo crítico en run_quick_analysis: {e}")
        return {
            "success": False,
            "error": str(e)
        }
