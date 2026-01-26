# -*- coding: utf-8 -*-
"""
Corrective Agent - Red de seguridad que refina búsquedas fallidas.
"""

import json
from typing import List, Dict

from src.agents.base_agent import BaseAgent
from src.graph.state import WorkflowState, SubQuery
from src.utils.llm_config import generate_response


class CorrectiveAgent(BaseAgent):
    """
    Agent correctivo que:
    1. Analiza por qué falló la búsqueda (Evaluation Report)
    2. Identifica información faltante
    3. Genera nuevas sub-queries optimizadas
    4. Incrementa contador de reintentos
    """
    
    def __init__(self):
        super().__init__(name="corrective")
    
    def run(self, state: WorkflowState) -> WorkflowState:
        """
        Ejecuta la lógica de re-planificación correctiva.
        """
        self.log_start(state)
        
        try:
            # Incrementar contadores
            iteration = state.get("corrective_iteration", 0) + 1
            retry_count = state.get("retry_count", 0) + 1
            
            state["corrective_iteration"] = iteration
            state["retry_count"] = retry_count
            
            # Recuperar contexto del fallo
            report = state.get("evaluation_report", {})
            missing_info = report.get("missing_info", [])
            query = state["query"]
            
            self.logger.info(f"Iniciando corrección iteración {iteration}. Faltan: {missing_info}")
            
            # Generar queries refinadas con GPT-4o
            new_sub_queries = self._generate_refined_queries(query, missing_info, iteration)
            
            # Actualizar sub_queries en el estado para que RetrievalAgent las ejecute
            # IMPORTANTE: Reemplazamos las anteriores o las agregamos?
            # Estrategia: Reemplazar sub_queries activas para la siguiente pasada de Retrieval.
            # Los chunks anteriores YA están en retrieved_chunks (es acumulativo).
            # Así que RetrievalAgent solo buscará lo nuevo.
            
            state["sub_queries"] = new_sub_queries
            
            # Registrar historial (opcional, para debug)
            idx_refined = state.get("refined_queries", [])
            idx_refined.extend([sq["query"] for sq in new_sub_queries])
            state["refined_queries"] = idx_refined
            
            # Instruir al grafo para volver a Retrieval
            state["next_agent"] = "retrieval"
            
            self.logger.info(f"Generadas {len(new_sub_queries)} queries refinadas. Volviendo a Retrieval.")
            self.log_end(state)
            
        except Exception as e:
            self.log_error(e)
            state["error"] = f"Correction failed: {str(e)}"
            # En caso de error fatal, abortar a Synthesis con lo que haya
            state["next_agent"] = "synthesis" # (Día 6)
        
        return state

    def _generate_refined_queries(self, original_query: str, missing_info: List[str], iteration: int) -> List[SubQuery]:
        """
        Usa GPT-4o para generar queries de búsqueda más efectivas.
        """
        
        missing_str = "\n".join([f"- {m}" for m in missing_info])
        
        prompt = f"""Actúa como experto en Recuperación de Información (Search Expert).
Nuestra búsqueda inicial falló en encontrar toda la información necesaria.

CONSULTA ORIGINAL: "{original_query}"

INFORMACIÓN FALTANTE (Reportada por el Auditor):
{missing_str}

TU TAREA:
Generar nuevas sub-queries de búsqueda ALTAMENTE ESPECÍFICAS para encontrar SOLO la información faltante.
Usa estrategias diferentes a la búsqueda semántica directa:
- Búsqueda por palabras clave específicas
- Sinónimos técnicos
- Expansión de términos

Iteración de corrección: {iteration}

FORMATO JSON ESPERADO:
{{
  "new_queries": [
    {{
      "query": "texto de la query refinada",
      "rationale": "estrategia usada (ej. uso de sinónimo técnico)"
    }},
    ...
  ]
}}

Genera máximo 3 queries refinadas. Responde SOLO con el JSON válido."""

        response = self.call_llm(prompt, max_tokens=500, temperature=0.3) # Un poco de creatividad para variar keywords
        
        try:
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_resp)
            
            # Convertir a formato SubQuery
            refined_sqs = []
            for i, item in enumerate(data.get("new_queries", [])):
                refined_sqs.append({
                    "id": 100 * iteration + i, # IDs únicos para diferenciar de ronda 1
                    "query": item["query"],
                    "rationale": f"[Refined Iter {iteration}] {item.get('rationale', '')}",
                    "dependency": []
                })
            
            # Fallback si el modelo no genera nada
            if not refined_sqs:
                self.logger.warning("Modelo no generó queries refinadas, reintentando con keywords genéricas")
                return self._fallback_queries(missing_info)
                
            return refined_sqs
            
        except Exception as e:
            self.logger.error(f"Error parseando queries refinadas: {e}")
            return self._fallback_queries(missing_info)
    
    def _fallback_queries(self, missing_info: List[str]) -> List[SubQuery]:
        """Queries de respaldo simples."""
        return [{
            "id": 999,
            "query": f"detalles sobre {m}", 
            "rationale": "Fallback keyword search",
            "dependency": []
        } for m in missing_info[:3]]
