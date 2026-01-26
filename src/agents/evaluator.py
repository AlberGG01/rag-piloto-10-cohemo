# -*- coding: utf-8 -*-
"""
Evaluation Agent - Auditor de calidad (Self-Critique).
Juzga si la información recuperada es suficiente para responder la query.
"""

import json
from typing import List, Dict

from src.agents.base_agent import BaseAgent
from src.graph.state import WorkflowState, EvaluationReport
from src.utils.llm_config import generate_response


class EvaluationAgent(BaseAgent):
    """
    Agent auditor que:
    1. Analiza los chunks recuperados vs las sub-queries requeridas
    2. Determina si falta información crítica
    3. Emite un veredicto (SUFFICIENT/PARTIAL/INSUFFICIENT)
    """
    
    def __init__(self):
        super().__init__(name="evaluator")
    
    def run(self, state: WorkflowState) -> WorkflowState:
        """
        Ejecuta la evaluación de suficiencia.
        """
        self.log_start(state)
        
        try:
            query = state["query"]
            sub_queries = state.get("sub_queries", [])
            chunks = state.get("retrieved_chunks", [])
            
            # Si no hay chunks, es insuficiente automáticamente
            if not chunks:
                self.logger.warning("No hay chunks para evaluar.")
                report = {
                    "status": "INSUFFICIENT",
                    "reasoning": "La búsqueda no retornó ningún documento.",
                    "missing_info": [sq["query"] for sq in sub_queries],
                    "score": 0.0
                }
                state["evaluation_report"] = report
                state["is_sufficient"] = False
                state["next_agent"] = "corrective"  # O replanner
                return state
            
            # Preparar contexto para el LLM
            # Resumir chunks para evitar context limit excesivo (solo contenido clave)
            context_summary = self._summarize_context(chunks)
            
            # Ejecutar evaluación con GPT-4o
            report = self._evaluate_sufficiency(query, sub_queries, context_summary)
            
            # Actualizar estado
            state["evaluation_report"] = report
            state["evaluation_score"] = report["score"]
            state["is_sufficient"] = report["status"] == "SUFFICIENT"
            
            self.logger.info(f"Evaluación completada: {report['status']} (Score: {report['score']})")
            
            # Decisión de routing
            if report["status"] == "SUFFICIENT":
                state["next_agent"] = "synthesis"  # (Día 6)
            else:
                # Si es partial/insufficient, necesitamos corrección
                state["next_agent"] = "corrective" # (Día 5)
                # O podríamos terminar si ya iteramos demasiado (lógica que irá en el grafo)
            
            self.log_end(state)
            
        except Exception as e:
            self.log_error(e)
            state["error"] = f"Evaluation failed: {str(e)}"
            # Fallback seguro
            state["is_sufficient"] = False
            state["evaluation_report"] = {
                "status": "INSUFFICIENT", 
                "reasoning": f"Error: {str(e)}", 
                "missing_info": ["Evaluación fallida"],
                "score": 0.0
            }
        
        return state
    
    def _summarize_context(self, chunks: List[Dict]) -> str:
        """
        Genera un resumen ligero del contexto recuperado para el prompt.
        Solo incluye los primeros 200 caracteres de cada chunk para identificar de qué hablan.
        """
        summary = []
        for i, chunk in enumerate(chunks):
            content = chunk.get("contenido", "")[:200].replace("\n", " ")
            meta = chunk.get("metadata", {})
            source = meta.get("archivo", "unknown")
            section = meta.get("seccion", "general")
            summary.append(f"[{i+1}] {source} ({section}): {content}...")
        return "\n".join(summary)

    def _evaluate_sufficiency(self, query: str, sub_queries: List[Dict], context_str: str) -> EvaluationReport:
        """
        Usa GPT-4o para juzgar suficiencia.
        """
        
        sub_queries_text = "\n".join([f"- {sq['query']} ({sq['rationale']})" for sq in sub_queries])
        
        prompt = f"""Actúa como Auditor de Información para un sistema RAG de contratos de defensa.

TU TAREA:
Evaluar si la información recuperada (Contexto) es SUFICIENTE para responder rigurosamente a la Consulta del Usuario, basándote en los Requisitos (Sub-Queries) definidos.

CONSULTA ORIGINAL: "{query}"

REQUISITOS (SUB-QUERIES NECESARIAS):
{sub_queries_text}

CONTEXTO RECUPERADO (Resumen):
{context_str}

CRITERIOS DEEVALUACIÓN:
1. **SUFFICIENT**: Todos los datos clave para CADA sub-query están presentes. Podemos responder con certeza.
2. **PARTIAL**: Tenemos información para algunas sub-queries pero faltan datos críticos (ei. falta 1 contrato de 3, falta un importe).
3. **INSUFFICIENT**: Falta la mayoría de la información o la información recuperada es irrelevante.

IMPORTANTE:
- Sé estricto. Si piden "suma de todos los avales" y solo ves 1 aval pero hay menciones a otros contratos sin datos, es PARTIAL o INSUFFICIENT.
- No alucines información no presente.

FORMATO JSON ESPERADO:
{{
  "status": "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT",
  "reasoning": "Explicación breve de por qué...",
  "missing_info": ["lista", "de", "datos", "faltantes"],
  "score": 0.0 a 100.0
}}

Responde SOLO con el JSON válido."""

        # Usar json_mode=True implícito via prompt engineering robusto o config si disponible
        # AHORA VIA call_llm para Rate Limit Protection
        response = self.call_llm(prompt, max_tokens=500, temperature=0.0)
        
        try:
            clean_resp = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_resp)
            return {
                "status": data.get("status", "INSUFFICIENT"),
                "reasoning": data.get("reasoning", "No reasoning provided"),
                "missing_info": data.get("missing_info", []),
                "score": float(data.get("score", 0.0))
            }
        except Exception as e:
            self.logger.error(f"Error parseando JSON de evaluación: {e}")
            return {
                "status": "INSUFFICIENT",
                "reasoning": "Error parseando respuesta del auditor",
                "missing_info": ["Evaluación fallida"],
                "score": 0.0
            }
