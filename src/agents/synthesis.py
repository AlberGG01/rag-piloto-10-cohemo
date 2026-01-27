# -*- coding: utf-8 -*-
"""
Synthesis Agent - Generador de respuesta final con citas.
"""

from typing import List, Dict

from src.agents.base_agent import BaseAgent
from src.graph.state import WorkflowState
from src.utils.llm_config import generate_response


class SynthesisAgent(BaseAgent):
    """
    Agent sintetizador que:
    1. Recopila todo el contexto recuperado (chunks)
    2. Revisa el reporte de evaluación para gaps
    3. Genera respuesta final con citas rigurosas
    """
    
    def __init__(self):
        super().__init__(name="synthesis")
    
    def run(self, state: WorkflowState) -> WorkflowState:
        """
        Ejecuta la síntesis final.
        """
        self.log_start(state)
        
        try:
            query = state["query"]
            chunks = state.get("retrieved_chunks", [])
            eval_report = state.get("evaluation_report", {})
            
            # 1. Token Budgeting: Recortar contexto si excede límite
            from src.utils.token_counter import trim_context
            chunks_processed = trim_context(chunks, max_tokens=20000)
            
            if len(chunks_processed) < len(chunks):
                self.logger.warning(f"Contexto recortado: {len(chunks)} -> {len(chunks_processed)} chunks")

            # Preparar contexto y mapa de fuentes
            # --- U-SHAPE REORDERING (MITIGATE LOST IN THE MIDDLE) ---
            chunks_reordered = self._reorder_chunks_u_shape(chunks_processed)
            context_str, source_map = self._format_context_with_citations(chunks_reordered)
            
            # --- DEBUG: Ver el mapa de reemplazo ---
            print(f"DEBUG SOURCE MAP: {source_map}")
            # ---------------------------------------
            
            # Identificar gaps
            missing_info = []
            if eval_report:
                missing_info = eval_report.get("missing_info", [])
                status = eval_report.get("status", "UNKNOWN")
            
            # Generar respuesta (con referencias "Documento X")
            raw_answer = self._generate_answer(query, context_str, missing_info, status if eval_report else "UNKNOWN")
            
            # --- NUCLEAR FIX: Reemplazar "Documento X" por Nombre Real ---
            final_answer = raw_answer
            for doc_key, real_source in source_map.items():
                # Reemplazar "Documento 1" por "NombreArchivo.pdf, Pág: X"
                # Usamos replace simple (cuidado con solapamientos si >10 documentos, pero asumimos <10 por top_k)
                # Mejoramos con regex para ser seguros
                import re
                # Patrón: Documento X (case insensitive)
                pattern = re.compile(re.escape(doc_key), re.IGNORECASE)
                replacement = f"Doc: {real_source}"
                final_answer = pattern.sub(replacement, final_answer)
            
            # Limpieza final de formato "[Doc: Doc: file...]" si el LLM ya puso brackets
            final_answer = final_answer.replace("[Doc: Doc:", "[Doc:")
            
            # Actualizar estado
            state["final_answer"] = final_answer
            state["confidence"] = eval_report.get("score", 0.0) if eval_report else 0.0
            
            # Recopilar fuentes únicas para metadata
            sources = self._extract_sources(chunks_processed)
            state["sources"] = sources
            
            # Fin del workflow
            state["next_agent"] = "end"
            
            self.logger.info("Síntesis completada exitosamente.")
            self.log_end(state)
            
        except Exception as e:
            self.log_error(e)
            state["error"] = f"Synthesis failed: {str(e)}"
            state["final_answer"] = "Lo siento, hubo un error técnico generando la respuesta final."
        
        return state

    def _format_context_with_citations(self, chunks: List[Dict]) -> Tuple[str, Dict[str, str]]:
        """
        Formatea chunks numerados explícitamente para que el LLM los cite fácil,
        y devuelve un mapa para reemplazar la referencia numérica por el nombre real después.
        """
        formatted = []
        source_map = {}
        
        for i, chunk in enumerate(chunks, 1):
            content = chunk.get("contenido", "").strip()
            meta = chunk.get("metadata", {})
            real_filename = meta.get("archivo") or meta.get("source") or "Desconocido.pdf"
            pagina = meta.get("pagina", "?")
            
            # Clave que el LLM usará
            doc_key = f"Documento {i}"
            
            # Guardar mapeo: "Documento 1" -> "real_filename.pdf"
            source_map[doc_key] = f"{real_filename}, Pág: {pagina}"
            
            # Formato simple para el LLM
            block = (
                f"--- {doc_key} ---\n"
                f"CONTENIDO:\n{content}\n"
            )
            formatted.append(block)
            
        return "\n\n".join(formatted), source_map

    def _generate_answer(self, query: str, context: str, missing: List[str], quality_status: str) -> str:
        """
        Genera la respuesta con GPT-4o.
        """
        
        missing_instruction = ""
        if missing:
            missing_instruction = f"""
ADVERTENCIA IMPORTANTE:
El auditor detectó que FALTA información sobre: {', '.join(missing)}.
Debes mencionar explícitamente en tu respuesta que NO se encontró esta información específica.
NO inventes ni asumas datos que no están en el contexto.
"""

        prompt = f"""Actúa como Analista Senior de Defensa. Tu tarea es responder a la consulta del usuario basándote EXCLUSIVAMENTE en los documentos proporcionados.

CONSULTA: "{query}"

CONTEXTO DISPONIBLE (Ordenado por Relevancia Estratégica: Inicio y Final son CRÍTICOS):
{context}

INSTRUCCIONES DE REDACCIÓN:
1. **Precisión Absoluta**: Usa solo la información del contexto. Si algo no está, dilo.
2. **Citas Obligatorias**: CADA afirmación debe llevar una cita al final.
   - Usa EXCLUSIVAMENTE el formato: [Documento X].
   - NO intentes poner el nombre del archivo. Solo pon el número del documento.
   - Ejemplo: "El importe es de 20M€ [Documento 1]."
   - Si combinas info: "Según [Documento 1] y [Documento 2]..."
3. **Estilo Profesional Markdown**:
   - Usa ## Títulos claros
   - Usa listas con viñetas para enumerar datos
   - Usa **negritas** para cifras o entidades clave
   - Usa tablas si hay datos comparativos
4. **Responde Directamente**: Empieza con la respuesta directa a la pregunta.
   - Usa **negritas** para cifras o entidades clave
   - Usa tablas si hay datos comparativos
4. **Responde Directamente**: Empieza con la respuesta directa a la pregunta.

{missing_instruction}

Genera la respuesta final ahora:"""

        return self.call_llm(prompt, max_tokens=2000, temperature=0.0)

    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Extrae lista de fuentes únicas."""
        sources = {}
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            archivo = meta.get("archivo", "unknown")
            if archivo not in sources:
                sources[archivo] = {
                    "archivo": archivo,
                    "paginas": set()
                }
            if "pagina" in meta:
                sources[archivo]["paginas"].add(meta["pagina"])
        
        return [
            {"archivo": k, "paginas": sorted(list(v["paginas"]))}
            for k, v in sources.items()
        ]

    def _reorder_chunks_u_shape(self, chunks: List[Dict]) -> List[Dict]:
        """
        Reordena chunks para poner los más relevantes al INICIO y al FINAL.
        Estrategia: Top 5 -> Inicio, Siguientes 5 -> Final, Resto -> Medio.
        Objetivo: Mitigar 'Lost in the Middle' phenomenon.
        """
        if not chunks:
            return []
            
        # Asumimos que chunks entran ordenados por score (Highest -> Lowest)
        
        if len(chunks) <= 5:
            return chunks
            
        top_5 = chunks[:5]
        next_5 = chunks[5:10] if len(chunks) > 5 else []
        rest = chunks[10:] if len(chunks) > 10 else []
        
        # [TOP 5] + [BASURA/MEDIO] + [TOP 6-10]
        # De esta forma los mejores están donde el LLM presta más atención
        reordered = top_5 + rest + next_5
        
        return reordered
