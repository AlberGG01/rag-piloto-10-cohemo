# -*- coding: utf-8 -*-
"""
Retrieval Agent - Ejecuta sub-queries en paralelo y reporta hallazgos.
"""

import concurrent.futures
from typing import List, Dict, Any
from collections import defaultdict

from src.agents.base_agent import BaseAgent
from src.graph.state import WorkflowState, SubQuery
from src.utils.smart_retrieval import smart_hierarchical_retrieval


class RetrievalAgent(BaseAgent):
    """
    Agent de recuperación que:
    1. Recibe lista de sub-queries del planner
    2. Ejecuta búsquedas en paralelo (ThreadPool)
    3. Genera reporte de hallazgos (Finding Report)
    4. Acumula chunks en el estado
    """
    
    def __init__(self, max_workers: int = 5):
        super().__init__(name="retrieval")
        self.max_workers = max_workers
    
    def run(self, state: WorkflowState) -> WorkflowState:
        """
        Ejecuta retrieval paralelo.
        """
        self.log_start(state)
        
        try:
            sub_queries = state.get("sub_queries", [])
            if not sub_queries:
                # Fallback predeterminado si no hay sub-queries (usar query original)
                sub_queries = [{
                    "id": 0,
                    "query": state["query"],
                    "rationale": "Direct query fallback",
                    "dependency": []
                }]
            
            self.logger.info(f"Iniciando retrieval paralelo para {len(sub_queries)} sub-queries...")
            
            # Ejecutar en paralelo
            all_chunks = []
            finding_reports = {}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Mapear sub-query a futuro
                future_to_sq = {
                    executor.submit(self._execute_single_retrieval, sq): sq 
                    for sq in sub_queries
                }
                
                for future in concurrent.futures.as_completed(future_to_sq):
                    sq = future_to_sq[future]
                    try:
                        chunks, report = future.result()
                        all_chunks.extend(chunks)
                        finding_reports[sq["id"]] = report
                    except Exception as e:
                        self.log_error(f"Error en sub-query {sq['id']}: {e}")
                        finding_reports[sq["id"]] = {
                            "status": "Error",
                            "chunks_found": 0,
                            "message": str(e)
                        }
            
            # Deduplicar chunks (por contenido hash o ID si tuviéramos)
            # Usamos contenido para deduplicar simple
            unique_chunks = []
            seen_content = set()
            
            for chunk in all_chunks:
                content_hash = hash(chunk["contenido"])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    unique_chunks.append(chunk)
            
            self.logger.info(f"Recuperados {len(unique_chunks)} chunks únicos totales")
            
            # Actualizar estado
            # Nota: retrieved_chunks es Annotated[List, add], así que extendemos
            # Pero para evitar duplicados con ejecuciones previas (si las hubiera), 
            # podríamos querer reemplazar o filtrar.
            # Dado el diseño de LangGraph state, retornamos la *diferencia* o el valor completo si es overwrite.
            # En este caso state.py define 'retrieved_chunks: Annotated[List[Dict], add]'
            # Si retornamos la lista, se agrega a la existente.
            # Como este agent corre una vez por iteración (o en corrective), está bien agregar.
            
            # REVISION: Si el grafo cicla, retrieved_chunks crecerá indefinidamente.
            # Para Día 3, asumimos flujo lineal o controlado.
            
            state["retrieved_chunks"] = unique_chunks
            
            # Actualizar metadata de retrieval
            state["retrieval_metadata"] = {
                "finding_reports": finding_reports,
                "total_chunks": len(unique_chunks)
            }
            
            # Siguiente paso
            state["next_agent"] = "evaluator"  # (A implementar en Día 4)
            
            self.log_end(state)
            
        except Exception as e:
            self.log_error(e)
            state["error"] = f"Retrieval failed: {str(e)}"
        
        return state

    def _execute_single_retrieval(self, sub_query: SubQuery) -> tuple[List[Dict], Dict]:
        """
        Ejecuta una única sub-query y genera su reporte.
        """
        query_text = sub_query["query"]
        sq_id = sub_query["id"]
        
        self.logger.debug(f"Ejecutando SQ-{sq_id}: {query_text}")
        
        # Usar smart retrieval
        # Ajustar parámetros según el tipo de query si fuera posible, por ahora defaults
        chunks = smart_hierarchical_retrieval(
            query=query_text,
            top_docs=10,  # Un poco menos restrictivo por sub-query
            chunks_per_doc=3
        )
        
        # Generar Reporte de Hallazgo
        status = "No Encontrado"
        msg = "No se encontraron documentos relevantes."
        
        if chunks:
            if len(chunks) >= 5: # Umbral arbitrario de "buen" retrieval
                status = "Encontrado"
                msg = f"Se encontraron {len(chunks)} chunks relevantes."
            else:
                status = "Parcial"
                msg = f"Solo se encontraron {len(chunks)} chunks (posible información incompleta)."
        
        # Detección de "No Encontrado" específico
        # Si Smart Retrieval retornó vacío, ya logueó warning.
        # Aquí podemos ser más específicos si smart_retrieval retornara por qué falló (filtros muy estrictos, etc)
        # Por ahora nos basamos en results.
        
        report = {
            "query": query_text,
            "status": status,
            "chunks_found": len(chunks),
            "message": msg
        }
        
        return chunks, report
