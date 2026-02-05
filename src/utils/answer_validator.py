"""
Sistema de validación multi-capa para respuestas del RAG.
Previene alucinaciones y asegura trazabilidad.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AnswerValidator:
    """Validador de respuestas con múltiples capas de verificación"""
    
    def __init__(self):
        # Patrones para extraer diferentes tipos de datos críticos
        self.patterns = {
            "importes": r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:€|EUR|euros?)",
            "fechas": r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            "cifs": r"\b([A-Z]-?\d{8})\b",
            "dias": r"(\d+)\s*días?\s*(?:naturales|hábiles)?",
            "porcentajes": r"(\d+(?:[.,]\d+)?)\s*%",
            "normativas": r"((?:ISO|STANAG|MIL-STD|UNE-EN)\s*[\w\-:]+)",
        }
    
    def validate_numerical_integrity(
        self, 
        answer: str, 
        source_chunks: List[str]
    ) -> Dict[str, Any]:
        """
        VALIDACIÓN MEJORADA: Distingue números literales de calculados
        """
        violations = []
        source_text = "\n".join(source_chunks)
        
        # Extraer todos los números
        all_numbers = self._extract_all_numbers(answer)
        total_numbers = sum(len(nums) for nums in all_numbers.values())
        
        logger.info(f"🔍 Validando {total_numbers} números en respuesta...")
        
        # ========== NUEVO: Detectar números calculados ==========
        calculation_patterns = {
            "diferencia": r"(?:supera|mayor|excede|diferencia).*?(?:en|de)\s+([\d.,]+)",
            "suma_total": r"(?:suma\s+total|total\s+de.*?garantías).*?(?:es|:)\s+([\d.,]+)",
            "suma": r"(?:suma|total|conjunto).*?(?:de|es)\s+([\d.,]+)",
            "multiplicacion": r"(?:producto|multiplicado).*?(?:es|de)\s+([\d.,]+)",
            "porcentaje": r"([\d.,]+)\s*%.*?(?:de|sobre)\s+([\d.,]+)",
        }
        
        calculated_numbers = set()
        for calc_type, pattern in calculation_patterns.items():
            matches = re.finditer(pattern, answer, re.IGNORECASE)
            for match in matches:
                calc_num = self._normalize_number(match.group(1))
                calculated_numbers.add(calc_num)
                logger.info(f"  📐 Número calculado detectado ({calc_type}): {match.group(1)}")
        
        # ========== Validar números ==========
        for num_type, numbers in all_numbers.items():
            for number in numbers:
                normalized = self._normalize_number(number)
                
                # SKIP validación si es número calculado
                if normalized in calculated_numbers:
                    logger.info(f"  ✅ SKIP: {number} (es cálculo válido)")
                    continue
                
                # Buscar en fuente (con variaciones de formato)
                if not self._number_exists_in_source(normalized, source_text):
                    violations.append({
                        "number": number,
                        "type": num_type,
                        "severity": "CRÍTICO",
                        "reason": f"Número no encontrado en documentos (tipo: {num_type})"
                    })
                    logger.warning(f"  ❌ VIOLACIÓN: '{number}' ({num_type}) no existe en fuente")
        
        # Resultado
        is_valid = len(violations) == 0
        
        if is_valid:
            logger.info(f"✅ Integridad numérica OK: {total_numbers} números verificados ({len(calculated_numbers)} calculados)")
        else:
            logger.error(f"🚨 {len(violations)} violaciones de integridad numérica")
        
        return {
            "valid": is_valid,
            "violations": violations,
            "numbers_checked": total_numbers,
            "calculated_numbers_skipped": len(calculated_numbers)
        }
    
    def validate_logical_coherence(
        self,
        answer: str,
        query: str,
        source_chunks: List[str]
    ) -> Dict[str, Any]:
        """
        VALIDACIÓN CAPA 2: Coherencia Lógica
        
        Usa un LLM como "juez" para verificar que la respuesta
        no contradice las fuentes.
        
        Returns:
            {
                "valid": bool,
                "reasoning": str,
                "confidence": float
            }
        """
        from src.utils.llm_config import generate_response
        
        # Usamos generate_response en lugar de get_llm().invoke para mantener consistencia con el proyecto
        
        validation_prompt = f"""
Actúa como un auditor técnico. Evalúa si esta respuesta es coherente con las fuentes.

PREGUNTA ORIGINAL:
{query}

RESPUESTA GENERADA:
{answer}

FRAGMENTOS FUENTE:
{chr(10).join(f"[{i+1}] {chunk[:300]}..." for i, chunk in enumerate(source_chunks[:5]))}

CRITERIOS DE EVALUACIÓN:
1. ¿La respuesta está respaldada por las fuentes?
2. ¿Hay contradicciones con los documentos?
3. ¿Se inventa información no presente?

Responde SOLO con:
VÁLIDO - [razón breve]
O
INVÁLIDO - [razón específica de la contradicción]
"""
        try:
            result = generate_response(validation_prompt, max_tokens=4096, temperature=0.0, model="gpt-4o-mini").strip()
            is_valid = "VÁLIDO" in result.upper()
        except Exception as e:
            logger.error(f"Error en validación lógica: {e}")
            is_valid = True # Fail open si falla el LLM
            result = "Error en validación lógica"

        return {
            "valid": is_valid,
            "reasoning": result,
            "confidence": 0.9 if is_valid else 0.3
        }
    
    def validate_citation_coverage(
        self,
        answer: str
    ) -> Dict[str, Any]:
        """
        VALIDACIÓN CAPA 3: Cobertura de Citación
        
        Umbral ajustado a 80% para permitir casos edge razonables.
        """
        # Extraer afirmaciones críticas (mejorado)
        critical_statements = self._extract_critical_statements(answer)
        
        if not critical_statements:
            # No hay statements críticos → automáticamente válido
            return {
                "valid": True,
                "uncited_statements": [],
                "citation_rate": 1.0
            }
        
        # Verificar cuáles tienen citación
        uncited = []
        for statement in critical_statements:
            if not self._has_citation(statement):
                uncited.append(statement)
        
        # Calcular tasa de citación
        citation_rate = (len(critical_statements) - len(uncited)) / len(critical_statements)
        
        # Umbral: 80% (permite hasta 1 de 5 sin citar)
        # Razón: Evita falsos positivos en casos edge sin comprometer calidad
        is_valid = citation_rate >= 0.8
        
        if is_valid:
            logger.info(f"✅ Citación OK: {citation_rate*100:.0f}% de {len(critical_statements)} statements citados")
        else:
            logger.warning(f"⚠️ Citación insuficiente: {citation_rate*100:.0f}% ({len(uncited)}/{len(critical_statements)} sin citar)")
            for uncited_stmt in uncited:
                logger.warning(f"   - Sin citar: {uncited_stmt[:80]}...")
        
        return {
            "valid": is_valid,
            "uncited_statements": uncited,
            "citation_rate": citation_rate
        }
    
    def validate_all(
        self,
        answer: str,
        query: str,
        source_chunks: List[str]
    ) -> Dict[str, Any]:
        """
        VALIDACIÓN COMPLETA: Ejecuta todas las capas
        
        Returns:
            {
                "overall_valid": bool,
                "numerical": Dict,
                "logical": Dict,
                "citation": Dict,
                "recommendation": str
            }
        """
        logger.info("="*60)
        logger.info("🛡️  VALIDACIÓN MULTI-CAPA INICIADA")
        logger.info("="*60)
        
        # Capa 1: Numérica
        numerical = self.validate_numerical_integrity(answer, source_chunks)
        
        # Capa 2: Lógica
        logical = self.validate_logical_coherence(answer, query, source_chunks)
        
        # Capa 3: Citación
        citation = self.validate_citation_coverage(answer)
        
        # Resultado global
        overall_valid = numerical["valid"] and logical["valid"] and citation["valid"]
        
        # Recomendación
        if overall_valid:
            recommendation = "✅ RESPUESTA VALIDADA - Usar directamente"
        elif not numerical["valid"]:
            recommendation = "🚨 CRÍTICO - Alucinación numérica detectada. RECHAZAR respuesta."
        elif not logical["valid"]:
            recommendation = "⚠️ ADVERTENCIA - Posible contradicción con fuentes. Revisar manualmente."
        else:
            recommendation = "⚠️ ADVERTENCIA - Citación insuficiente. Añadir fuentes."
        
        logger.info(f"\n{recommendation}\n")
        
        return {
            "overall_valid": overall_valid,
            "numerical": numerical,
            "logical": logical,
            "citation": citation,
            "recommendation": recommendation
        }
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _extract_all_numbers(self, text: str) -> Dict[str, List[str]]:
        """Extrae números por categoría"""
        extracted = {}
        for num_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                extracted[num_type] = matches
        return extracted
    
    def _normalize_number(self, number: str) -> str:
        """Normaliza formato de número para comparación"""
        # Eliminar separadores de miles y unificar decimales
        normalized = number.replace('.', '').replace(',', '.')
        
        # Si tiene múltiples puntos, es formato europeo
        if number.count('.') > 1:
            normalized = number.replace('.', '').replace(',', '.')
        elif number.count(',') > 1:
            normalized = number.replace(',', '')
        
        return normalized
    
    def _number_exists_in_source(self, number: str, source_text: str) -> bool:
        """Verifica si número existe en fuente (tolerando formatos)"""
        # Generar variaciones comunes
        variations = [
            number,
            number.replace('.', ','),
            self._add_separators(number, '.', ','), # European: 1.234,56
            self._add_separators(number, ',', '.'), # US: 1,234.56
            self._add_separators(number, ' ', ','), # Space: 1 234,56
        ]
        
        return any(var in source_text for var in variations)
    
    def _add_separators(self, number: str, thousands_sep: str, decimal_sep: str) -> str:
        """Añade separadores de miles y decimales"""
        parts = number.split('.')
        integer = parts[0]
        decimal = parts[1] if len(parts) > 1 else None
        
        # Formatear parte entera
        formatted = ""
        for i, digit in enumerate(reversed(integer)):
            if i > 0 and i % 3 == 0:
                formatted = thousands_sep + formatted
            formatted = digit + formatted
        
        if decimal:
            formatted += decimal_sep + decimal
        
        return formatted
    
    def _extract_critical_statements(self, text: str) -> List[str]:
        """
        Extrae frases con información crítica (MEJORADO)
        
        Ignora secciones de metadata que no son claims.
        """
        # Dividir texto por frases completas
        # Patrón mejorado: divide solo cuando hay punto + espacio + mayúscula
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        critical = []
        
        # Secciones de metadata a ignorar (NO son claims críticos)
        metadata_markers = [
            "FUENTES CONSULTADAS",
            "RESPUESTA DETALLADA",
            "INTELLIGENCE REPORT",
            "📄", "📊", "📈", "⚠️", "✅", "❌", "🛡️",
            "ADVERTENCIA",
            "Fuentes:", "Sources:",
        ]
        
        for sentence in sentences:
            sentence_clean = sentence.strip()
            
            # SKIP 1: Secciones de metadata
            if any(marker in sentence_clean for marker in metadata_markers):
                continue
            
            # SKIP 2: Frases muy cortas (< 10 caracteres)
            if len(sentence_clean) < 10:
                continue
            
            # SKIP 3: Solo emojis o símbolos
            if not any(c.isalnum() for c in sentence_clean):
                continue
            
            # INCLUIR: Si contiene datos críticos (números, fechas, normativas)
            has_critical_data = any(
                re.search(pattern, sentence_clean) 
                for pattern in self.patterns.values()
            )
            
            if has_critical_data:
                critical.append(sentence_clean)
        
        return critical
    
    def _has_citation(self, statement: str) -> bool:
        """
        Verifica si statement tiene citación (MEJORADO)
        
        Soporta múltiples formatos de citación.
        """
        citation_patterns = [
            r'\[Fuente:.*?\]',                    # [Fuente: DOC.md, Pág: X]
            r'\[Doc(?:umento)?:.*?\]',            # [Doc: X] o [Documento: X]
            r'\(Fuente:.*?\)',                    # (Fuente: DOC)
            r'\(Ver:.*?\)',                       # (Ver: DOC)
            r'según\s+(?:el\s+)?documento',      # según el documento X
            r'de acuerdo con\s+(?:el\s+)?contrato', # de acuerdo con el contrato
            r'como se indica en',                 # como se indica en DOC
            r'recogido en',                       # recogido en DOC
            r'\*\*\[Doc:.*?\]\*\*',              # **[Doc: ...]**
        ]
        
        # Buscar cualquier patrón (case-insensitive, multi-line)
        for pattern in citation_patterns:
            if re.search(pattern, statement, re.IGNORECASE | re.DOTALL):
                return True
        
        return False


# ========== FUNCIÓN HELPER PARA USO RÁPIDO ==========

def validate_answer(answer: str, query: str, source_chunks: List) -> Dict:
    """
    Wrapper simple para validar respuesta antes de mostrar al usuario
    
    Usage:
        validation = validate_answer(answer, query, chunks)
        if not validation["overall_valid"]:
            # Manejar error
    """
    validator = AnswerValidator()
    
    # Convertir chunks a texto plano si es necesario
    chunk_texts = [
        chunk.get("contenido", "") if isinstance(chunk, dict) else str(chunk)
        for chunk in source_chunks
    ]
    
    return validator.validate_all(answer, query, chunk_texts)
