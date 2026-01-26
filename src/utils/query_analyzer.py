# -*- coding: utf-8 -*-
"""
Query Analyzer - Mapea queries a filtros de metadata inteligentes
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def analyze_query_for_filters(query: str) -> Optional[Dict]:
    """
    Analiza una query y retorna filtros de metadata apropiados.
    
    Args:
        query: Query del usuario
    
    Returns:
        Dict con filtros de ChromaDB o None si no aplica filtro
    """
    
    query_lower = query.lower()
    filters = {}
    
    # Detección de tipo de información solicitada
    
    # 1. Queries sobre avales/garantías
    if any(keyword in query_lower for keyword in ['aval', 'garantía', 'garantia', 'avalista']):
        filters['contiene_aval'] = True
        logger.info("🎯 Query sobre avales - filtrando chunks con contiene_aval=True")
    
    # 2. Queries sobre clasificación de seguridad
    elif any(keyword in query_lower for keyword in ['secreto', 'confidencial', 'clasificación', 'clasificacion']):
        filters['contiene_clasificacion'] = True
        logger.info("🎯 Query sobre clasificación - filtrando chunks con contiene_clasificacion=True")
    
    # 3. Queries sobre códigos NSN
    elif any(keyword in query_lower for keyword in ['nsn', 'código nsn', 'codigo nsn']):
        filters['contiene_nsn'] = True
        logger.info("🎯 Query sobre NSN - filtrando chunks con contiene_nsn=True")
    
    # 4. Queries sobre normativas STANAG
    elif 'stanag' in query_lower:
        filters['contiene_stanag'] = True
        logger.info("🎯 Query sobre STANAG - filtrando chunks con contiene_stanag=True")
    
    # 5. Queries sobre penalizaciones
    elif any(keyword in query_lower for keyword in ['penalización', 'penalizacion', 'retraso']):
        filters['contiene_penalizacion'] = True
        logger.info("🎯 Query sobre penalizaciones - filtrando chunks con contiene_penalizacion=True")
    
    # 6. Queries sobre subcontratación
    elif any(keyword in query_lower for keyword in ['subcontratación', 'subcontratacion', 'subcontratar']):
        filters['contiene_subcontratacion'] = True
        logger.info("🎯 Query sobre subcontratación - filtrando chunks con contiene_subcontratacion=True")
    
    # 7. Queries sobre importes/económicas (solo si no es de avales, prioridad a avales)
    elif any(keyword in query_lower for keyword in ['importe', 'precio', 'coste', 'costo', 'económica', 'economica']):
        filters['tipo_seccion'] = 'economicas'
        logger.info("🎯 Query sobre importes - filtrando tipo_seccion=economicas")
    
    # 8. Queries sobre fechas/plazos
    elif any(keyword in query_lower for keyword in ['fecha', 'plazo', 'vencimiento', 'cuando', 'cuándo']):
        filters['tipo_seccion'] = 'temporales'
        logger.info("🎯 Query sobre fechas/plazos - filtrando tipo_seccion=temporales")
    
    # Si no se detecta patrón específico, no filtrar (búsqueda abierta)
    if not filters:
        logger.info("💡 Query genérica - sin filtros de metadata")
        return None
    
    return filters


def apply_smart_filters(query: str, base_search_func):
    """
    Wrapper que aplica filtros inteligentes a una función de búsqueda.
    
    Args:
        query: Query del usuario
        base_search_func: Función de búsqueda base (ej: hierarchical_retrieval)
    
    Returns:
        Resultado de la búsqueda con filtros aplicados
    """
    
    filters = analyze_query_for_filters(query)
    
    if filters:
        # Aplicar búsqueda con filtros
        logger.info(f"Aplicando filtros: {filters}")
        # Nota: Necesitamos modificar hierarchical_retrieval para aceptar where_filter
        # Por ahora retornar los filtros para que el caller los use
        return filters
    
    return None
