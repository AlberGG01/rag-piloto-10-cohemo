import json
import logging
from typing import Dict, List, Optional, Any
from src.config import CLIENT, MODEL_FAST
from src.utils.deterministic_extractor import extract_cifs, extract_dates, extract_contract_ids

logger = logging.getLogger(__name__)

class QueryAnalyzer:
    """
    Agente de Entendimiento de Query (Query Understanding Layer).
    Analiza la intención del usuario, extrae entidades y planifica la estrategia de recuperación.
    """
    
    def __init__(self):
        self.model = MODEL_FAST # Usamos gpt-4o-mini por eficiencia y baja latencia
        
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Analiza la query y devuelve un plan estructurado.
        """
        try:
            # 1. Extracción determinista rápida (Regex)
            # Esto ayuda al LLM y sirve de fallback de seguridad
            det_cifs = extract_cifs(query)
            det_dates = extract_dates(query)
            det_contracts = extract_contract_ids(query)
            
            # 2. Análisis semántico con LLM
            prompt = self._build_prompt(query)
            response = CLIENT.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de consultas para un sistema RAG de contratos de defensa. Tu salida es JSON puro."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # 3. Fusión de datos (Prioridad Regex para exactitud)
            analysis["entities"]["cifs"] = list(set(analysis.get("entities", {}).get("cifs", []) + det_cifs))
            analysis["entities"]["contract_ids"] = list(set(analysis.get("entities", {}).get("contract_ids", []) + det_contracts))
            # Fechas es más complejo de fusionar, dejamos las del LLM si las estructuró bien (ej. rangos)
            
            # 4. Corrección para Comparaciones: Evitar filtro único si la intención es comparar
            if analysis.get("query_type") == "COMPARISON":
                if "filters" in analysis:
                    analysis["filters"]["contract_id"] = None
            
            logger.info(f"🧠 Query Analyzed: {analysis.get('query_type')} | Intent: {analysis.get('intent')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error en QueryAnalyzer: {e}")
            # Fallback seguro
            return {
                "query_type": "GENERAL",
                "intent": "search",
                "entities": {
                    "cifs": extract_cifs(query),
                    "contract_ids": extract_contract_ids(query)
                },
                "filters": {},
                "sub_queries": [query]
            }

    def _build_prompt(self, query: str) -> str:
        return f"""
        Analiza la siguiente consulta de usuario para un sistema de contratos de defensa.
        
        CONSULTA: "{query}"
        
        INSTRUCCIONES CLAVE PARA ENTIDADES:
        - CONTRACT_IDS: Solo códigos con formato estricto XXX_YYYY_NNN (ej: CON_2024_001). NO incluyas palabras genéricas (ej: "Ciberseguridad", "Mantenimiento") aquí.
        - TOPICS/CONCEPTOS: Temas o categorías generales (ej: "ciberseguridad", "vehículos").
        - NORMATIVAS: Estándares técnicos (ej: ISO 9001, STANAG 4569).
        
        Genera un JSON con la siguiente estructura:
        {{
            "query_type": "FACTUAL" | "AGGREGATION" | "COMPARISON" | "TEMPORAL" | "LIST",
            "intent": "Descripción breve de la intención (ej: 'extraer_importe', 'listar_contratos')",
            "entities": {{
                "cifs": ["LISTA DE CIFs"],
                "contract_ids": ["LISTA DE IDs DE CONTRATO (Solo códigos XXX_YYYY_NNN)"],
                "fechas": ["LISTA DE FECHAS"],
                "normativas": ["LISTA DE NORMATIVAS"],
                "conceptos_clave": ["LISTA DE TOPICS/KEYWORDS"]
            }},
            "filters": {{
                "year": numerico o null,
                "contract_id": string (Solo si es un ID válido XXX_YYYY_NNN) o null,
                "entidad": string o null
            }},
            "is_complex": boolean,
            "search_strategy": "SINGLE_DOC" | "MULTI_DOC" | "EXHAUSTIVE_SCAN"
        }}
        
        EJEMPLOS:
        Query: "¿Cuál es el importe del contrato CON_2024_001?"
        {{
            "query_type": "FACTUAL",
            "intent": "extract_amount",
            "entities": {{"contract_ids": ["CON_2024_001"]}},
            "filters": {{"contract_id": "CON_2024_001"}},
            "is_complex": false,
            "search_strategy": "SINGLE_DOC"
        }}
        
        Query: "Compara el contrato de Ciberseguridad con el de Visión Nocturna"
        {{
            "query_type": "COMPARISON",
            "intent": "compare_contracts_by_topic",
            "entities": {{"conceptos_clave": ["Ciberseguridad", "Visión Nocturna"], "contract_ids": []}},
            "filters": {{"contract_id": null}},
            "is_complex": true,
            "search_strategy": "MULTI_DOC"
        }}
        """
