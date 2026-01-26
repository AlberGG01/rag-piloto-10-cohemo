# -*- coding: utf-8 -*-
"""
Enriquecimiento automático de metadata para chunks.
Detecta tipo de contenido y etiqueta chunks inteligentemente.
"""

import re
from typing import Dict

def enrich_chunk_metadata(chunk_text: str, section_name: str, base_metadata: Dict) -> Dict:
    """
    Enriquece la metadata de un chunk con detección automática de contenido.
    
    Args:
        chunk_text: Contenido del chunk
        section_name: Nombre de la sección
        base_metadata: Metadata base del documento
    
    Returns:
        Dict: Metadata enriquecida
    """
    
    enriched = base_metadata.copy()
    
    # Normalizar tipo de sección
    section_lower = section_name.lower()
    
    if any(keyword in section_lower for keyword in ['garantía', 'garantia', 'aval']):
        enriched['tipo_seccion'] = 'garantias'
    elif any(keyword in section_lower for keyword in ['importe', 'económica', 'economica', 'pago']):
        enriched['tipo_seccion'] = 'economicas'
    elif any(keyword in section_lower for keyword in ['fecha', 'plazo', 'hito']):
        enriched['tipo_seccion'] = 'temporales'
    elif any(keyword in section_lower for keyword in ['nsn', 'código', 'codigo', 'stanag']):
        enriched['tipo_seccion'] = 'codigos'
    elif any(keyword in section_lower for keyword in ['metadata', 'expediente']):
        enriched['tipo_seccion'] = 'metadata'
    elif any(keyword in section_lower for keyword in ['objeto', 'descripción', 'descripcion']):
        enriched['tipo_seccion'] = 'descripcion'
    elif any(keyword in section_lower for keyword in ['cláusula',  'clausula', 'obligación', 'obligacion']):
        enriched['tipo_seccion'] = 'clausulas'
    elif any(keyword in section_lower for keyword in ['norma', 'certificación', 'certificacion']):
        enriched['tipo_seccion'] = 'normas'
    else:
        enriched['tipo_seccion'] = 'general'
    
    # Detectar contenido específico
    chunk_lower = chunk_text.lower()
    
    # Contiene información de avales/garantías
    enriched['contiene_aval'] = any(keyword in chunk_lower for keyword in [
        'aval', 'garantía', 'garantia', 'aval bancario', 'entidad avalista'
    ])
    
    # Contiene importes monetarios
    enriched['contiene_importe'] = bool(
        re.search(r'\d+[.,]\d+[.,]?\d*\s*(eur|€)', chunk_lower) or
        re.search(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*(eur|€)', chunk_lower)
    )
    
    # Contiene fechas
    enriched['contiene_fecha'] = bool(
        re.search(r'\d{1,2}/\d{1,2}/\d{4}', chunk_text) or
        re.search(r'\d{4}-\d{2}-\d{2}', chunk_text)
    )
    
    # Contiene códigos NSN
    enriched['contiene_nsn'] = 'nsn' in chunk_lower or bool(
        re.search(r'nsn-?\d+', chunk_lower)
    )
    
    # Contiene códigos STANAG
    enriched['contiene_stanag'] = 'stanag' in chunk_lower or bool(
        re.search(r'stanag[-\s]?\d+', chunk_lower)
    )
    
    # Contiene información de clasificación de seguridad
    enriched['contiene_clasificacion'] = any(keyword in chunk_lower for keyword in [
        'secreto', 'confidencial', 'reservado', 'clasificación', 'clasificacion'
    ])
    
    # Detectar entidades bancarias mencionadas
    bancos = ['santander', 'bbva', 'caixabank', 'la caixa', 'sabadell', 
              'bankinter', 'kutxabank', 'liberbank', 'ing bank', 'unicaja']
    entidades_encontradas = [banco for banco in bancos if banco in chunk_lower]
    if entidades_encontradas:
        enriched['entidades_bancarias'] = entidades_encontradas
    
    # Extraer importes específicos (para búsquedas numéricas)
    importes = re.findall(r'(\d+[.,]\d+[.,]?\d*)\s*(?:eur|€)', chunk_lower)
    if importes:
        # Convertir a floatsintentando normalizar formato
        try:
            importes_normalizados = []
            for imp in importes[:5]:  # Máximo 5 importes
                normalized = imp.replace('.', '').replace(',', '.')
                importes_normalizados.append(float(normalized))
            enriched['importes_encontrados'] = importes_normalizados
        except:
            pass
    
    # Marcadores de contenido crítico
    enriched['contiene_penalizacion'] = 'penalización' in chunk_lower or 'penalizacion' in chunk_lower
    enriched['contiene_subcontratacion'] = 'subcontratación' in chunk_lower or 'subcontratacion' in chunk_lower
    
    return enriched
