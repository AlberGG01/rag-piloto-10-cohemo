# -*- coding: utf-8 -*-
"""
Agente Analizador: Detecta alertas críticas comparando fechas y condiciones.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import ALERT_DAYS_HIGH, ALERT_DAYS_MEDIUM, ALERT_DAYS_MILESTONE

logger = logging.getLogger(__name__)


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parsea una fecha en formato DD/MM/YYYY.
    
    Args:
        date_string: Fecha en formato string.
    
    Returns:
        datetime: Fecha parseada o None si falla.
    """
    if not date_string or date_string == "null":
        return None
    
    # Limpiar la cadena
    date_string = str(date_string).strip()
    
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d.%m.%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None


def calculate_days_until(date: datetime) -> int:
    """
    Calcula los días hasta una fecha desde hoy.
    
    Args:
        date: Fecha objetivo.
    
    Returns:
        int: Número de días (negativo si ya pasó).
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = date - today
    return delta.days


def get_priority(days: int) -> str:
    """
    Determina la prioridad según los días restantes.
    
    Args:
        days: Días hasta el vencimiento.
    
    Returns:
        str: Emoji + texto de prioridad.
    """
    if days <= ALERT_DAYS_HIGH:
        return "🔴 Alta"
    elif days <= ALERT_DAYS_MEDIUM:
        return "🟡 Media"
    else:
        return "🟢 Baja"


def analyze_contract(contract_data: Dict) -> List[Dict]:
    """
    Analiza un contrato y genera alertas si corresponde.
    
    Args:
        contract_data: Datos extraídos del contrato.
    
    Returns:
        List[Dict]: Lista de alertas detectadas.
    """
    alerts = []
    
    expediente = contract_data.get("num_expediente") or contract_data.get("_archivo", "Desconocido")
    archivo = contract_data.get("_archivo", "")
    
    # 1. Verificar vencimiento del contrato
    fecha_fin = parse_date(contract_data.get("fecha_fin"))
    if fecha_fin:
        days = calculate_days_until(fecha_fin)
        if days <= ALERT_DAYS_MEDIUM and days >= 0:
            alerts.append({
                "expediente": expediente,
                "observacion": f"El contrato vence en {days} días ({fecha_fin.strftime('%d/%m/%Y')})",
                "accion": "Evaluar renovación o preparar cierre del contrato",
                "prioridad": get_priority(days),
                "dias": days,
                "tipo": "vencimiento_contrato"
            })
        elif days < 0:
            alerts.append({
                "expediente": expediente,
                "observacion": f"El contrato venció hace {abs(days)} días ({fecha_fin.strftime('%d/%m/%Y')})",
                "accion": "URGENTE: Revisar estado del contrato vencido",
                "prioridad": "🔴 Alta",
                "dias": days,
                "tipo": "contrato_vencido"
            })
    
    # 2. Verificar vencimiento del aval
    aval_vencimiento = parse_date(contract_data.get("aval_vencimiento"))
    if aval_vencimiento:
        days = calculate_days_until(aval_vencimiento)
        aval_importe = contract_data.get("aval_importe", "")
        aval_entidad = contract_data.get("aval_entidad", "")
        
        if days <= ALERT_DAYS_MEDIUM and days >= 0:
            obs = f"El aval bancario"
            if aval_importe:
                obs += f" de {aval_importe}"
            if aval_entidad:
                obs += f" ({aval_entidad})"
            obs += f" vence en {days} días"
            
            alerts.append({
                "expediente": expediente,
                "observacion": obs,
                "accion": "Contactar con el banco para renovación del aval",
                "prioridad": get_priority(days),
                "dias": days,
                "tipo": "vencimiento_aval"
            })
        elif days < 0:
            alerts.append({
                "expediente": expediente,
                "observacion": f"El aval bancario venció hace {abs(days)} días",
                "accion": "URGENTE: Renovar aval inmediatamente",
                "prioridad": "🔴 Alta",
                "dias": days,
                "tipo": "aval_vencido"
            })
    
    # 3. Verificar hitos de entrega próximos
    hitos = contract_data.get("hitos_entrega", [])
    if isinstance(hitos, list):
        for hito in hitos:
            if isinstance(hito, dict):
                hito_fecha = parse_date(hito.get("fecha"))
                hito_desc = hito.get("descripcion", "Hito de entrega")
                
                if hito_fecha:
                    days = calculate_days_until(hito_fecha)
                    if days <= ALERT_DAYS_MILESTONE and days >= 0:
                        alerts.append({
                            "expediente": expediente,
                            "observacion": f"Hito de entrega próximo: {hito_desc} en {days} días",
                            "accion": "Verificar estado de cumplimiento del hito",
                            "prioridad": get_priority(days),
                            "dias": days,
                            "tipo": "hito_proximo"
                        })
    
    # 4. Verificar si no permite revisión de precios
    permite_revision = contract_data.get("permite_revision_precios")
    if permite_revision is False or str(permite_revision).lower() == "false":
        alerts.append({
            "expediente": expediente,
            "observacion": "El contrato no permite revisión de precios",
            "accion": "Evaluar riesgo de inflación en este contrato",
            "prioridad": "🟢 Baja",
            "dias": 999,  # Para ordenar al final
            "tipo": "sin_revision_precios"
        })
    
    # 5. Verificar cláusula de confidencialidad
    requiere_conf = contract_data.get("requiere_confidencialidad")
    if requiere_conf is True or str(requiere_conf).lower() == "true":
        alerts.append({
            "expediente": expediente,
            "observacion": "Contrato con cláusula de confidencialidad activa",
            "accion": "Verificar habilitación de seguridad del personal asignado",
            "prioridad": "🟡 Media",
            "dias": 998,  # Para ordenar después de urgentes
            "tipo": "confidencialidad"
        })
    
    return alerts


def analyze_all_contracts(extracted_data: List[Dict]) -> List[Dict]:
    """
    Analiza todos los contratos extraídos y genera alertas.
    
    Args:
        extracted_data: Lista de datos extraídos de contratos.
    
    Returns:
        List[Dict]: Lista de todas las alertas ordenadas por prioridad.
    """
    all_alerts = []
    
    for contract_data in extracted_data:
        alerts = analyze_contract(contract_data)
        all_alerts.extend(alerts)
    
    # Ordenar por días (más urgentes primero)
    all_alerts.sort(key=lambda x: (x["dias"], x["tipo"]))
    
    logger.info(f"Análisis completado: {len(all_alerts)} alertas detectadas")
    return all_alerts


def run_analyzer_node(state: Dict) -> Dict:
    """
    Nodo del grafo LangGraph: Ejecuta el análisis de alertas.
    
    Args:
        state: Estado actual del grafo (debe contener 'extracted_data').
    
    Returns:
        Dict: Estado actualizado con alertas detectadas.
    """
    logger.info("=== AGENTE ANALIZADOR: Iniciando análisis ===")
    
    extracted_data = state.get("extracted_data", [])
    
    if not extracted_data:
        logger.warning("No hay datos extraídos para analizar")
        return {
            **state,
            "alerts": [],
            "analysis_complete": True
        }
    
    alerts = analyze_all_contracts(extracted_data)
    
    # Contar por prioridad
    high_count = sum(1 for a in alerts if "🔴" in a["prioridad"])
    medium_count = sum(1 for a in alerts if "🟡" in a["prioridad"])
    low_count = sum(1 for a in alerts if "🟢" in a["prioridad"])
    
    return {
        **state,
        "alerts": alerts,
        "alerts_summary": {
            "total": len(alerts),
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        },
        "analysis_complete": True
    }
