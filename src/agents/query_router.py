import re
from typing import Literal, Dict

QueryComplexity = Literal["SIMPLE", "MEDIUM", "COMPLEX"]

class QueryRouter:
    """
    Clasifica queries por complejidad para optimizar recursos.
    """
    
    # Patrones de complejidad
    AGGREGATION_WORDS = [
        "todos", "cuántos", "cuáles", "lista", "listado",
        "total", "suma", "cada", "enumera"
    ]
    
    COMPARISON_WORDS = [
        "compara", "comparación", "diferencia", "vs", "versus",
        "entre", "mejor", "peor", "mayor", "menor"
    ]
    
    SIMPLE_PATTERNS = [
        r'\bCIF\b',
        r'\bfecha\b',
        r'\bimporte\b',
        r'\bproveedor\b',
        r'\bcontrato\s+\w+',  # "contrato CON_2024_001"
    ]

    TECHNICAL_EXTRACTION_PATTERNS = [
        r'\bCIF\b',
        r'\bISO\s+\d+',
        r'\bSTANAG\s+\d+',
        r'\bnormativa\b',
        r'\bcertificación\b',
    ]
    
    def classify(self, query: str) -> QueryComplexity:
        """
        Clasifica la query en SIMPLE/MEDIUM/COMPLEX.
        
        SIMPLE: Búsqueda de dato único identificado
        MEDIUM: Comparativas, análisis de 2-3 entidades
        COMPLEX: Agregaciones, listas exhaustivas, multi-criterio
        """
        query_lower = query.lower()
        
        # 1. COMPLEX: Agregaciones (prioridad máxima)
        if any(word in query_lower for word in self.AGGREGATION_WORDS):
            return "COMPLEX"
        
        # 2. COMPLEX: Multi-criterio (Y/E/TAMBIÉN)
        if self._has_multiple_criteria(query):
            return "COMPLEX"
        
        # 3. MEDIUM: Comparativas
        if any(word in query_lower for word in self.COMPARISON_WORDS):
            return "MEDIUM"
        
        # 3.5. MEDIUM: Extracciones Técnicas (Upgrade desde SIMPLE)
        # Si busca CIF o Normativas, gpt-4o-mini (SIMPLE) a veces falla. Usamos MEDIUM.
        has_technical = any(
            re.search(p, query, re.I) 
            for p in self.TECHNICAL_EXTRACTION_PATTERNS
        )
        if has_technical and len(query.split()) <= 20:
            return "MEDIUM"

        # 4. SIMPLE: Patrón de búsqueda directa + query corta
        if self._is_direct_lookup(query):
            return "SIMPLE"
        
        # 5. DEFAULT: MEDIUM (seguro)
        return "MEDIUM"
    
    def _has_multiple_criteria(self, query: str) -> bool:
        """Detecta queries con múltiples criterios técnicos."""
        # Contar criterios técnicos (ISO, STANAG, etc)
        # Búsqueda más laxa: "ISO 9001", "ISO9001", solo "ISO", solo "STANAG"
        iso_count = len(re.findall(r'\bISO\b', query, re.I))
        stanag_count = len(re.findall(r'\bSTANAG\b', query, re.I))
        
        # Si tiene 2+ criterios técnicos distintos
        criteria_count = iso_count + stanag_count
        if criteria_count >= 2:
            return True

        # O si tiene conectores lógicos Y/E relevantes
        # "contratos ISO y STANAG" -> COMPLEX
        # "contratos de limpieza y mantenimiento" -> COMPLEX (potencialmente)
        has_logical_and = re.search(r'\b(y|e|también|además)\b', query, re.I)
        
        # Si menciona al menos una norma Y tiene un "y/e"
        if (iso_count > 0 or stanag_count > 0) and has_logical_and:
            return True
            
        return False
    
    def _is_direct_lookup(self, query: str) -> bool:
        """Detecta si es búsqueda de dato único."""
        # Debe tener patrón simple
        has_simple_pattern = any(
            re.search(p, query, re.I) 
            for p in self.SIMPLE_PATTERNS
        )
        
        # Y ser query corta (< 12 palabras)
        is_short = len(query.split()) <= 12
        
        return has_simple_pattern and is_short
    
    def get_config(self, complexity: QueryComplexity) -> Dict:
        """
        Retorna configuración óptima según complejidad.
        """
        configs = {
            "SIMPLE": {
                "top_k": 5,
                "use_reranker": False,
                "model": "gpt-4o-mini",
                "temperature": 0.0,
                "expected_latency": "3-8s",
                "cost_multiplier": 0.1  # 10% del coste normal
            },
            "MEDIUM": {
                "top_k": 15,
                "use_reranker": False,
                "model": "gpt-4o-mini",
                "temperature": 0.0,
                "expected_latency": "8-20s",
                "cost_multiplier": 0.15
            },
            "COMPLEX": {
                "top_k": 30,
                "use_reranker": True,
                "model": "gpt-4o",
                "temperature": 0.0,
                "expected_latency": "60-180s",
                "cost_multiplier": 1.0
            }
        }
        
        return configs[complexity]
