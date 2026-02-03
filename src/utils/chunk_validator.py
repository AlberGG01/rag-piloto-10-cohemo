# -*- coding: utf-8 -*-
"""
Validador de Chunks - Rule-Based
Blindaje contra chunks vacíos, corruptos o con metadata incompleta.
Ejecución: <100ms para 1000 chunks (sin LLM).
"""
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def validate_chunk(chunk: Dict, strict: bool = False) -> Tuple[bool, str]:
    """
    Valida un chunk individual con reglas programáticas.
    
    Args:
        chunk: Diccionario con 'contenido' y 'metadata'
        strict: Si True, rechaza chunks con warnings menores
    
    Returns:
        (is_valid, reason): Tupla con resultado y motivo de rechazo
    """
    content = chunk.get("contenido", "")
    metadata = chunk.get("metadata", {})
    source = metadata.get("source", "UNKNOWN")
    
    # ═══════════════════════════════════════════════════
    # CHECK 1: Contenido no vacío (CRÍTICO)
    # ═══════════════════════════════════════════════════
    if not content or len(content.strip()) < 10:
        return False, f"Contenido vacío o muy corto ({len(content)} chars)"
    
    # ═══════════════════════════════════════════════════
    # CHECK 2: Metadata obligatoria (CRÍTICO)
    # ═══════════════════════════════════════════════════
    required_keys = ["source"]
    missing = [k for k in required_keys if k not in metadata]
    if missing:
        return False, f"Metadata incompleta: falta {missing}"
    
    # ═══════════════════════════════════════════════════
    # CHECK 3: Encoding corrupto (CRÍTICO)
    # ═══════════════════════════════════════════════════
    if content.count("�") > 5:  # Más de 5 caracteres de reemplazo
        return False, f"Encoding corrupto: {content.count('�')} caracteres '�'"
    
    # ═══════════════════════════════════════════════════
    # CHECK 4: Contenido solo espacios/saltos (WARNING)
    # ═══════════════════════════════════════════════════
    if content.replace("\n", "").replace(" ", "").replace("\r", "") == "":
        return False, "Contenido solo whitespace"
    
    # ═══════════════════════════════════════════════════
    # CHECK 5: Proporción de caracteres no-ASCII (WARNING)
    # ═══════════════════════════════════════════════════
    non_ascii = sum(1 for c in content if ord(c) > 127)
    if non_ascii / len(content) > 0.5 and strict:
        return False, f"Demasiados caracteres no-ASCII ({non_ascii}/{len(content)})"
    
    return True, "OK"


def validate_chunks_batch(chunks: List[Dict], abort_threshold: float = 0.1) -> Tuple[List[Dict], Dict]:
    """
    Valida un batch de chunks y reporta estadísticas.
    
    Args:
        chunks: Lista de chunks a validar
        abort_threshold: Si % de fallos > threshold, aborta con excepción
    
    Returns:
        (valid_chunks, stats): Chunks válidos + estadísticas de validación
    
    Raises:
        ValueError: Si % de fallos excede abort_threshold
    """
    if not chunks:
        logger.warning("⚠️ validate_chunks_batch: lista vacía")
        return [], {"total": 0, "valid": 0, "invalid": 0, "errors": {}}
    
    valid_chunks = []
    invalid_count = 0
    error_reasons = {}
    
    for i, chunk in enumerate(chunks):
        is_valid, reason = validate_chunk(chunk)
        
        if is_valid:
            valid_chunks.append(chunk)
        else:
            invalid_count += 1
            source = chunk.get("metadata", {}).get("source", f"chunk_{i}")
            
            # Agrupar por tipo de error
            error_reasons[reason] = error_reasons.get(reason, 0) + 1
            
            # Log detallado
            logger.warning(f"⚠️ Chunk inválido [{source}]: {reason}")
    
    # Calcular estadísticas
    total = len(chunks)
    valid = len(valid_chunks)
    invalid_pct = (invalid_count / total) * 100
    
    stats = {
        "total": total,
        "valid": valid,
        "invalid": invalid_count,
        "invalid_pct": invalid_pct,
        "errors": error_reasons
    }
    
    # Log resumen
    logger.info(f"📊 Validación de chunks: {valid}/{total} válidos ({100-invalid_pct:.1f}%)")
    if error_reasons:
        logger.info(f"   Errores detectados: {error_reasons}")
    
    # ═══════════════════════════════════════════════════
    # ABORT SI DEMASIADOS FALLOS (protección)
    # ═══════════════════════════════════════════════════
    if invalid_pct > (abort_threshold * 100):
        raise ValueError(
            f"❌ VALIDACIÓN FALLIDA: {invalid_count}/{total} chunks inválidos ({invalid_pct:.1f}%)\n"
            f"   Threshold: {abort_threshold*100}%\n"
            f"   Errores: {error_reasons}\n"
            f"   🔧 Revisa el proceso de chunking o el archivo fuente."
        )
    
    return valid_chunks, stats


def validate_chunk_content_quality(content: str) -> Dict[str, any]:
    """
    Análisis de calidad del contenido (métricas adicionales).
    Útil para debugging, NO bloquea la ingestión.
    
    Returns:
        Dict con métricas: avg_word_len, has_numbers, has_dates, etc.
    """
    words = content.split()
    
    return {
        "char_count": len(content),
        "word_count": len(words),
        "avg_word_len": sum(len(w) for w in words) / len(words) if words else 0,
        "has_numbers": any(c.isdigit() for c in content),
        "has_uppercase": any(c.isupper() for c in content),
        "line_count": content.count("\n") + 1,
        "unique_chars": len(set(content))
    }
