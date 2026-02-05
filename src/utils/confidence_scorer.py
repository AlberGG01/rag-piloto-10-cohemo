"""
Sistema de scoring de confianza para respuestas del RAG.
Combina múltiples señales para calcular confianza 0-100%.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    """Calcula confianza de respuesta basándose en múltiples factores"""
    
    def __init__(self):
        # Pesos de cada factor (suman 100)
        self.weights = {
            "retrieval_quality": 30,    # Calidad del top chunk
            "consensus": 25,             # Acuerdo entre chunks
            "specificity": 20,           # Respuesta concreta vs genérica
            "validation": 25             # Resultados del validator
        }
    
    def detect_query_type(self, query: str) -> str:
        """Detecta el tipo de query para aplicar lógica de confianza correcta"""
        
        aggregative_keywords = [
            "todos", "todas", "lista", "identifica",
            "suma", "total", "cuenta", "cuántos",
            "desglosa", "desglose", "completa"
        ]
        
        comparative_keywords = [
            "compara", "comparación", "diferencia",
            "versus", "vs", "entre"
        ]
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in aggregative_keywords):
            return "aggregative"
        elif any(kw in query_lower for kw in comparative_keywords):
            return "comparative"
        else:
            return "specific"

    def calculate_aggregative_confidence(
        self,
        answer: str,
        query: str,
        chunks_with_scores: List[tuple],
        validation_result: Dict
    ) -> Dict:
        """Calcula confianza para queries agregativas (con validaciones)"""
        
        # Validación defensiva
        if not chunks_with_scores:
            return {
                "confidence": 0.0,
                "breakdown": {},
                "items_found": 0,
                "error": "No chunks for aggregative query"
            }
        
        try:
            # Factor 1: Coverage (60%) - ¿Cuántos items únicos?
            # Extraer metadatos de los chunks
            sources = []
            for chunk, _ in chunks_with_scores:
                if isinstance(chunk, dict):
                    meta = chunk.get("metadata", {})
                else:
                     # Langchain doc object
                    meta = getattr(chunk, "metadata", {})
                
                source = meta.get("archivo") or meta.get("source") or ""
                if source:
                    sources.append(source)
                    
            unique_sources = len(set(sources))
            
            # Estimar total esperado (heurística)
            if "todos" in query.lower() or "todas" in query.lower():
                estimated_total = 20  # Ajustar según tu caso
            else:
                estimated_total = unique_sources # Asumir recuperó todos si no es exhaustivo
            
            # Evitar división por cero
            estimated_total = max(1, estimated_total)

            coverage = min(100, (unique_sources / estimated_total) * 100)
            
            # Factor 2: Validation (30%)
            validation_score = 100 if validation_result and validation_result.get("overall_valid") else 0
            
            # Factor 3: Completeness (10%)
            summary_keywords = ["total", "suma", "resumen", "en total", "en conjunto"]
            has_summary = any(kw in answer.lower() for kw in summary_keywords)
            completeness = 100 if has_summary else 50
            
            # Calcular confianza final
            confidence = (
                coverage * 0.6 +
                validation_score * 0.3 +
                completeness * 0.1
            )
            
            breakdown = {
                "coverage": round(coverage, 1),
                "validation": round(validation_score, 1),
                "completeness": round(completeness, 1)
            }
            
            return {
                "confidence": round(confidence, 1),
                "breakdown": breakdown,
                "items_found": unique_sources,
                "estimated_total": estimated_total,
                "query_type": "aggregative"
            }
        except Exception as e:
            logger.error(f"❌ Error en calculate_aggregative_confidence: {e}")
            return {
                "confidence": 0.0,
                "breakdown": {},
                "items_found": 0,
                "error": str(e)
            }

    def score_answer(
        self,
        answer: str,
        query: str,
        chunks_with_scores: List[tuple],  # [(chunk, score), ...]
        validation_result: Dict = None
    ) -> Dict[str, Any]:
        """Calcula score de confianza 0-100%"""
        logger.info("🎯 Calculando confidence score...")
        
        # Detectar tipo de query
        query_type = self.detect_query_type(query)
        logger.info(f"📋 Tipo de query detectado: {query_type}")
        
        if query_type == "aggregative":
            # Usar lógica específica para agregativas
            result = self.calculate_aggregative_confidence(
                answer, query, chunks_with_scores, validation_result
            )
            confidence = result["confidence"]
            breakdown = result["breakdown"]
            recommendation = self._get_recommendation(confidence, breakdown, query_type)
            
            logger.info(f"📊 Breakdown (Agregativo): {breakdown}")
            logger.info(f"🎯 Confidence final: {confidence:.1f}%")
            
            return {
                "confidence": confidence,
                "breakdown": breakdown,
                "recommendation": recommendation,
                "factors": {
                    "query_type": query_type,
                    "items_found": result["items_found"],
                    "top_chunk_score": chunks_with_scores[0][1] if chunks_with_scores else 0.0,
                    "chunks_analyzed": len(chunks_with_scores)
                }
            }
        else:
            # Lógica original (Specific)
            return self._score_specific_answer(answer, query, chunks_with_scores, validation_result)

    def _score_specific_answer(
        self,
        answer: str,
        query: str,
        chunks_with_scores: List[tuple],
        validation_result: Dict = None
    ) -> Dict[str, Any]:
        """Lógica original de scoring para queries específicas"""
        
        # Factor 1: Calidad del Retrieval
        retrieval_score = self._score_retrieval_quality(chunks_with_scores)
        
        # Factor 2: Consenso entre chunks
        consensus_score = self._score_consensus(answer, chunks_with_scores)
        
        # Factor 3: Especificidad de la respuesta
        specificity_score = self._score_specificity(answer, query)
        
        # Factor 4: Validación (si está disponible)
        if validation_result:
            validation_score = self._score_validation(validation_result)
        else:
            validation_score = 50  # Neutral si no hay validación
        
        # Calcular score ponderado
        breakdown = {
            "retrieval_quality": retrieval_score,
            "consensus": consensus_score,
            "specificity": specificity_score,
            "validation": validation_score
        }
        
        confidence = sum(
            (breakdown[factor] / 100) * self.weights[factor]
            for factor in self.weights
        )
        
        recommendation = self._get_recommendation(confidence, breakdown, "specific")
        
        logger.info(f"📊 Breakdown (Specific):")
        for factor, score in breakdown.items():
            logger.info(f"  - {factor}: {score}/100")
        logger.info(f"🎯 Confidence final: {confidence:.1f}%")
        
        return {
            "confidence": round(confidence, 1),
            "breakdown": breakdown,
            "recommendation": recommendation,
            "factors": {
                "top_chunk_score": chunks_with_scores[0][1] if chunks_with_scores else 0,
                "chunks_analyzed": len(chunks_with_scores)
            }
        }
    
    # ========== SCORING DE FACTORES INDIVIDUALES ==========
    
    def _score_retrieval_quality(self, chunks_with_scores: List[tuple]) -> int:
        """
        Score basado en calidad del top chunk
        
        Score > 0.9 → 100 puntos
        Score > 0.7 → 70 puntos
        Score > 0.5 → 40 puntos
        Score < 0.5 → 20 puntos
        """
        if not chunks_with_scores:
            return 0
        
        # Validar si chunks_with_scores tiene elementos y si estos tienen score
        try:
             top_score = chunks_with_scores[0][1]
        except (IndexError, TypeError):
             return 0

        
        if top_score >= 0.9:
            return 100
        elif top_score >= 0.7:
            return 70
        elif top_score >= 0.5:
            return 40
        else:
            return 20
    
    def _score_consensus(self, answer: str, chunks_with_scores: List[tuple]) -> int:
        """
        Score basado en consenso entre chunks
        
        Compara respuesta con múltiples chunks para ver si
        hay acuerdo en la información.
        """
        if len(chunks_with_scores) < 3:
            return 50  # Neutral si pocos chunks
        
        # Extraer entidades clave de la respuesta
        key_entities = self._extract_key_entities(answer)
        
        if not key_entities:
            return 50  # Neutral si no hay entidades específicas
        
        # Contar cuántos chunks contienen estas entidades
        top_chunks = chunks_with_scores[:5]  # Considerar top-5
        chunk_texts = [chunk[0].get("contenido", "") if isinstance(chunk[0], dict) else (chunk[0].page_content if hasattr(chunk[0], 'page_content') else str(chunk[0]))
                       for chunk in top_chunks]
        
        matches = 0
        for entity in key_entities:
            # Contar en cuántos chunks aparece
            count = sum(1 for text in chunk_texts if entity.lower() in text.lower())
            if count >= 2:  # Al menos 2 chunks confirman
                matches += 1
        
        # Score proporcional al consenso
        consensus_rate = matches / len(key_entities) if key_entities else 0
        
        if consensus_rate >= 0.8:
            return 100  # Alto consenso
        elif consensus_rate >= 0.5:
            return 70   # Consenso moderado
        elif consensus_rate >= 0.3:
            return 40   # Consenso bajo
        else:
            return 20   # Sin consenso
    
    def _score_specificity(self, answer: str, query: str) -> int:
        """
        Score basado en especificidad de la respuesta
        
        Penaliza respuestas genéricas tipo:
        - "No se encontró información"
        - "Según los documentos..."
        - Respuestas muy cortas (<20 palabras)
        """
        # Patrones de respuestas genéricas
        generic_patterns = [
            r"no\s+(?:se|está|consta|aparece|encuentra)",
            r"según\s+(?:el|los|la|las)\s+documento",
            r"puede\s+(?:consultar|ver|revisar)",
            r"información\s+no\s+disponible",
        ]
        
        # Penalizar si es genérica
        if any(re.search(p, answer.lower()) for p in generic_patterns):
            return 20
        
        # Penalizar respuestas muy cortas
        word_count = len(answer.split())
        if word_count < 20:
            return 40
        
        # Bonus por elementos específicos
        score = 60  # Base
        
        # +10 si tiene números
        if re.search(r'\d+', answer):
            score += 10
        
        # +10 si tiene fechas
        if re.search(r'\d{1,2}/\d{1,2}/\d{4}', answer):
            score += 10
        
        # +10 si tiene normativas (ISO, STANAG, etc)
        if re.search(r'(?:ISO|STANAG|MIL-STD|UNE-EN)\s*[\w\-:]+', answer):
            score += 10
        
        # +10 si tiene citaciones
        if re.search(r'\[(?:Doc|Fuente):', answer):
            score += 10
        
        return min(score, 100)
    
    def _score_validation(self, validation_result: Dict) -> int:
        """
        Score basado en resultados del Answer Validator
        
        100: Todas las capas válidas
        70: 2/3 capas válidas
        40: 1/3 capas válidas
        0: 0/3 capas válidas
        """
        valid_layers = sum([
            validation_result.get("numerical", {}).get("valid", False),
            validation_result.get("logical", {}).get("valid", False),
            validation_result.get("citation", {}).get("valid", False)
        ])
        
        if valid_layers == 3:
            return 100
        elif valid_layers == 2:
            return 70
        elif valid_layers == 1:
            return 40
        else:
            return 0
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _extract_key_entities(self, text: str) -> List[str]:
        """Extrae entidades clave (números, fechas, normativas, nombres)"""
        entities = []
        
        # Importes
        importes = re.findall(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*(?:€|EUR)', text)
        entities.extend(importes)
        
        # Fechas
        fechas = re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)
        entities.extend(fechas)
        
        # Normativas
        normativas = re.findall(r'(?:ISO|STANAG|MIL-STD|UNE-EN)\s*[\w\-:]+', text)
        entities.extend(normativas)
        
        # CIFs
        cifs = re.findall(r'\b[A-Z]-?\d{8}\b', text)
        entities.extend(cifs)
        
        # Contratos (ej: CON_2024_012)
        contratos = re.findall(r'[A-Z]{3}_\d{4}_\d{3}', text)
        entities.extend(contratos)
        
        return list(set(entities))  # Únicos
    
    def _get_recommendation(self, confidence: float, breakdown: Dict[str, int], query_type: str = "specific") -> str:
        """Genera recomendación legible"""
        
        if query_type == "aggregative":
            # Mensajes para queries agregativas
            if confidence >= 90:
                return "🟢 ALTA COBERTURA - Recuperó >90% de items esperados"
            elif confidence >= 70:
                return "🟢 BUENA COBERTURA - Recuperó ~70-90% de items"
            elif confidence >= 50:
                return "🟡 COBERTURA MEDIA - Recuperó ~50-70% de items"
            else:
                return "🔴 BAJA COBERTURA - Recuperó <50% de items"
        else:
            # Mensajes originales para queries específicas
            if confidence >= 90:
                return "✅ CONFIANZA ALTA - Usar directamente"
            elif confidence >= 70:
                return "🟢 CONFIANZA BUENA - Aceptable"
            elif confidence >= 50:
                return "🟡 CONFIANZA MEDIA - Revisar manualmente"
            else:
                return "🔴 CONFIANZA BAJA - Requiere validación humana"
    



# ========== FUNCIÓN HELPER ==========

def calculate_confidence(
    answer: str,
    query: str,
    chunks_with_scores: List[tuple],
    validation_result: Dict = None
) -> Dict:
    """
    Wrapper simple para calcular confianza
    
    Usage:
        confidence = calculate_confidence(answer, query, chunks, validation)
        print(f"Confianza: {confidence['confidence']}%")
    """
    scorer = ConfidenceScorer()
    return scorer.score_answer(answer, query, chunks_with_scores, validation_result)
