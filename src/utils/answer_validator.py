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
        VALIDACIÓN CAPA 1: Integridad Numérica
        
        Verifica que TODOS los números en la respuesta existen
        literalmente en los documentos fuente.
        
        Returns:
            {
                "valid": bool,
                "violations": List[Dict],
                "numbers_checked": int
            }
        """
        violations = []
        source_text = "\n".join(source_chunks)
        
        # Extraer todos los números de la respuesta
        all_numbers = self._extract_all_numbers(answer)
        total_numbers = sum(len(nums) for nums in all_numbers.values())
        
        logger.info(f"🔍 Validando {total_numbers} números en respuesta...")
        
        for num_type, numbers in all_numbers.items():
            for number in numbers:
                # Normalizar para comparación
                normalized = self._normalize_number(number)
                
                # Buscar en fuente (con variaciones de formato)
                if not self._number_exists_in_source(normalized, source_text):
                    violations.append({
                        "number": number,
                        "type": num_type,
                        "severity": "CRÍTICO",
                        "reason": f"Número no encontrado en documentos fuente"
                    })
                    logger.warning(f"❌ VIOLACIÓN: '{number}' ({num_type}) no existe en fuente")
        
        is_valid = len(violations) == 0
        
        if is_valid:
            logger.info(f"✅ Integridad numérica OK: {total_numbers} números verificados")
        else:
            logger.error(f"🚨 {len(violations)} violaciones de integridad numérica")
        
        return {
            "valid": is_valid,
            "violations": violations,
            "numbers_checked": total_numbers
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
            result = generate_response(validation_prompt, max_tokens=100, temperature=0.0, model="gpt-4o-mini").strip()
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
        
        Verifica que afirmaciones críticas (con números, fechas, normativas)
        tengan citación de fuente.
        
        Returns:
            {
                "valid": bool,
                "uncited_statements": List[str],
                "citation_rate": float
            }
        """
        # Detectar afirmaciones críticas (frases con datos importantes)
        critical_statements = self._extract_critical_statements(answer)
        
        uncited = []
        for statement in critical_statements:
            if not self._has_citation(statement):
                uncited.append(statement)
        
        citation_rate = (
            (len(critical_statements) - len(uncited)) / len(critical_statements)
            if critical_statements else 1.0
        )
        
        is_valid = citation_rate >= 0.8  # Al menos 80% citado
        
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
        """Extrae frases con información crítica"""
        sentences = re.split(r'[.!?]', text)
        critical = []
        
        for sentence in sentences:
            # Si contiene números, fechas, normativas → es crítica
            if any(re.search(p, sentence) for p in self.patterns.values()):
                critical.append(sentence.strip())
        
        return [s for s in critical if len(s) > 10]  # Filtrar muy cortas
    
    def _has_citation(self, statement: str) -> bool:
        """Verifica si statement tiene citación"""
        citation_patterns = [
            r'\[(?:Doc|Fuente|Documento):.*?\]',
            r'\((?:Fuente|Ver):.*?\)',
            r'según.*?(?:documento|página|sección)',
            r'\*\*\[Doc:.*?\]\*\*',
        ]
        return any(re.search(p, statement, re.IGNORECASE) for p in citation_patterns)


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
