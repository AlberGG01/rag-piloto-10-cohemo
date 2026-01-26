# -*- coding: utf-8 -*-
"""
Planning Agent - Analiza queries y genera plan de ejecución estructurado.
"""

from typing import List, Dict
import json
import re

from src.agents.base_agent import BaseAgent
from src.graph.state import WorkflowState, SubQuery
from src.utils.llm_config import generate_response


class PlanningAgent(BaseAgent):
    """
    Agent planner que:
    1. Clasifica complejidad de la query
    2. Descompone en sub-queries estructuradas
    3. Genera plan de ejecución
    """
    
    def __init__(self):
        super().__init__(name="planner")
    
    def run(self, state: WorkflowState) -> WorkflowState:
        """
        Analiza query y genera plan.
        """
        self.log_start(state)
        
        try:
            query = state["query"]
            
            # PASO 1: Clasificar complejidad
            complexity = self._classify_complexity(query)
            state["query_complexity"] = complexity
            
            self.logger.info(f"Complejidad detectada: {complexity}")
            
            # PASO 2: Descomponer en SubQueries estructuradas
            sub_queries = self._decompose_query_structured(query, complexity)
            state["sub_queries"] = sub_queries
            self.logger.info(f"Query descompuesta en {len(sub_queries)} sub-queries")
            
            # PASO 3: Generar plan de ejecución textual (para logging/debug)
            execution_plan = self._generate_execution_plan(query, complexity, sub_queries)
            state["execution_plan"] = execution_plan
            
            # Preparar siguiente agent
            state["next_agent"] = "retrieval"
            
            self.log_end(state)
            
        except Exception as e:
            self.log_error(e)
            state["error"] = f"Planning failed: {str(e)}"
            # Fallback: query simple estructurada
            state["query_complexity"] = "simple"
            state["sub_queries"] = [{
                "id": 1,
                "query": state["query"],
                "rationale": "Fallback por error en planner",
                "dependency": []
            }]
            state["execution_plan"] = "Fallback: búsqueda directa"
        
        return state
    
    def _classify_complexity(self, query: str) -> str:
        """
        Clasifica la complejidad de la query.
        """
        prompt = f"""Eres un experto en análisis de contratos. Clasifica la complejidad de esta consulta.

CONSULTA: "{query}"

TIPOS:
1. simple: Dato específico de un solo contrato.
2. multi-hop: Relacionar info de múltiples secciones o contratos.
3. aggregation: Sumar, contar, comparar o listar datos de múltiples documentos.

Responde SOLO con una palabra: simple, multi-hop, o aggregation"""

        response = self.call_llm(prompt, max_tokens=10, temperature=0.0)
        classification = response.strip().lower()
        
        if "simple" in classification: return "simple"
        if "multi" in classification: return "multi-hop"
        if "aggregation" in classification or "agregación" in classification: return "aggregation"
        return "simple"
    
    def _decompose_query_structured(self, query: str, complexity: str) -> List[SubQuery]:
        """
        Descompone query compleja en objetos SubQuery.
        """
        # Si es simple, no descomponer realmente
        if complexity == "simple":
            return [{
                "id": 1,
                "query": query,
                "rationale": "Consulta directa",
                "dependency": []
            }]

        prompt = f"""Actúa como Senior Planner. Descompón la CONSULTA en pasos atómicos para un sistema RAG.

CONSULTA: "{query}"
COMPLEJIDAD: {complexity}

INSTRUCCIONES:
1. Divide la consulta en sub-queries de recuperación de información.
2. Cada sub-query debe ser autosuficiente.
3. Para 'aggregation' (ej. suma de avales), genera una sub-query genérica que recupere TODOS los datos relevantes, o divídela por criterios si ayuda.
   - Mejor estrategia para suma: "Extraer importes de avales y garantías de todos los contratos disponibles"
4. Identifica dependencias si un paso requiere info del anterior.

FORMATO JSON ESPERADO:
{{
  "steps": [
    {{
      "id": 1,
      "query": "texto de la sub-query",
      "rationale": "por qué necesitamos esto"
    }},
    ...
  ]
}}

Responde SOLO con el JSON válido."""

        response = self.call_llm(prompt, max_tokens=1000, temperature=0.0)
        
        try:
            # Limpiar markdown code blocks
            clean_response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_response)
            steps = data.get("steps", [])
            
            sub_queries: List[SubQuery] = []
            for step in steps:
                sub_queries.append({
                    "id": step.get("id", 1),
                    "query": step.get("query", query),
                    "rationale": step.get("rationale", ""),
                    "dependency": step.get("dependency", [])
                })
            
            return sub_queries if sub_queries else self._fallback_subquery(query)
            
        except Exception as e:
            self.logger.error(f"Error parseando JSON del planner: {e}")
            self.logger.debug(f"Raw response: {response}")
            return self._fallback_subquery(query)

    def _fallback_subquery(self, query: str) -> List[SubQuery]:
        return [{
            "id": 1,
            "query": query,
            "rationale": "Fallback directo",
            "dependency": []
        }]
    
    def _generate_execution_plan(self, query: str, complexity: str, sub_queries: List[SubQuery]) -> str:
        """Genera plan textual."""
        lines = [f"PLAN ({complexity.upper()}): {query}"]
        for sq in sub_queries:
            dep = f" (Depende de: {sq['dependency']})" if sq['dependency'] else ""
            lines.append(f"{sq['id']}. {sq['query']} {dep}")
        return "\n".join(lines)
