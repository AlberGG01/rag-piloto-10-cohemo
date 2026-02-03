# -*- coding: utf-8 -*-
"""
Agente RAG v2.0: Chatbot Ultra-Rápido para consultas de contratos.
CAMBIOS CRÍTICOS:
- Zero PDF Processing en runtime (usa caché de metadatos)
- Búsqueda Híbrida FORZADA (Vector + BM25)
- Persistencia total (ChromaDB en disco)
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterator
import sys



sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from src.config import EXTRACTOR_PROMPT, RESPONDER_PROMPT, CONDENSED_QUESTION_PROMPT, MODEL_CHATBOT
from src.utils.vectorstore import is_vectorstore_initialized
from src.utils.hybrid_search import hybrid_search  # ÚNICO MOTOR DE BÚSQUEDA
from src.utils.reranker import rerank_chunks
from src.utils.llm_config import generate_response, is_model_available, generate_response_stream
from src.utils.deterministic_extractor import (
    extract_cif, extract_dates, extract_amounts, extract_normativas,
    extract_penalties, extract_contract_id, is_generic_iso_9001,
    contains_exact_amount, extract_final_execution_date
)
from src.agents.query_router import QueryRouter

logger = logging.getLogger(__name__)

# Caché de metadatos (generado offline por ingest_contracts.py)
METADATA_CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "metadata_cache.txt"

# Keywords para clasificar preguntas
QUANTITATIVE_KEYWORDS = [
    'importe', 'precio', 'coste', 'costar', 'valor', 'euros', 'millones',
    'mayor', 'menor', 'máximo', 'mínimo', 'total', 'suma',
    'fecha', 'vence', 'vencimiento', 'cuándo', 'plazo', 'días',
    'aval', 'garantía', 'banco', 'entidad',
    'cuántos', 'cuántas', 'lista', 'todos', 'resumen'
]

QUALITATIVE_KEYWORDS = [
    'describe', 'explica', 'detalle', 'objeto', 'qué incluye', 'servicios',
    'cláusula', 'condiciones', 'penalización', 'normas', 'requisitos',
    'confidencialidad', 'seguridad', 'subcontratación'
]

GREETING_KEYWORDS = [
    'hola', 'buenos días', 'buenas tardes', 'buenas noches', 'hey', 'hi',
    'qué tal', 'cómo estás', 'saludos', 'buenas'
]

HELP_KEYWORDS = [
    'qué puedes hacer', 'ayuda', 'help', 'qué haces', 'para qué sirves',
    'cómo funciona', 'qué me ofreces', 'ofertas', 'puedes ayudar'
]


def classify_query(query: str) -> str:
    """Clasifica la pregunta como GREETING, HELP, QUANTITATIVE o QUALITATIVE."""
    query_lower = query.lower().strip()
    
    if len(query_lower) < 30:
        for greeting in GREETING_KEYWORDS:
            if greeting in query_lower:
                return 'GREETING'
    
    for help_kw in HELP_KEYWORDS:
        if help_kw in query_lower:
            return 'HELP'
    
    quant_score = sum(1 for kw in QUANTITATIVE_KEYWORDS if kw in query_lower)
    qual_score = sum(1 for kw in QUALITATIVE_KEYWORDS if kw in query_lower)
    
    if qual_score > quant_score:
        return 'QUALITATIVE'
    return 'QUANTITATIVE'


def dynamic_top_k(query: str, query_type: str) -> int:
    """
    Determina el top_k óptimo basado en el tipo de query.
    
    Estrategia:
    - Queries exhaustivas ("todos", "lista"): 50 chunks (aumentado para cobertura total)
    - Queries de datos exactos ("exacto", "específico"): 10 chunks
    - Queries cuantitativas: 15 chunks
    - Queries con contrato específico: 10 chunks (filtrado)
    - Default: 15 chunks
    """
    query_lower = query.lower()
    
    # [Fase 3: Query Understanding Layer]
    # Analizamos la query para determinar estrategia
    from src.agents.query_analyzer import QueryAnalyzer
    
    analyzer = QueryAnalyzer()
    logger.info(f"🧠 Analizando query: '{query}'...")
    query_plan = analyzer.analyze(query)
    
    # 1. Ajuste de Top-K basado en Plan
    k = 30 # Default
    if query_plan.get("search_strategy") == "EXHAUSTIVE_SCAN" or query_plan.get("query_type") == "LIST":
         k = 50
         logger.info(f"🚀 Modo Exhaustivo Activado (k={k}) por Query Plan")
    elif query_plan.get("search_strategy") == "SINGLE_DOC":
         k = 15 # Optimización para dato puntual
         logger.info(f"⚡ Modo Single Doc Activado (k={k})")

    # 2. Extracción de filtros de metadatos del plan
    filter_metadata = None  # Ensure it is initialized
    plan_contracts = query_plan.get("entities", {}).get("contract_ids", [])
    
    if plan_contracts:
        # Si hay un contrato explícito, filtramos
        # Priorizamos el primero si hay varios y es SINGLE_DOC, o usamos lógica OR si soportada
        contract_id = plan_contracts[0] 
        filter_metadata = {"num_contrato": contract_id}
        logger.info(f"🎯 Filtro Metadata Activado: {contract_id}")

    
    # Detectar queries de precisión
    if any(kw in query_lower for kw in ["exacto", "específico", "preciso", "cuál es el"]):
        return 10
    
    # Detectar si menciona contrato específico
    if extract_contract_id(query):
        return 10  # Con filtrado de metadata, 10 es suficiente
    
    # Query cuantitativa
    if query_type == "QUANTITATIVE":
        return 15
        
    # Query cualitativa
    if query_type == "QUALITATIVE":
        return 15
    
    # Default (COMPLEX, SIMPLE, etc)
    return 15


def detect_exact_phrase_query(query: str) -> Optional[str]:
    """
    Detecta queries que requieren match de frase exacta.
    Retorna el pattern a buscar o None.
    
    Fase 2 P2: Búsqueda de frase exacta para EDGE_06.
    """
    exact_phrases = [
        (r'proh[íi]be?.*subcontrataci[óo]n', "subcontratación prohibida"),
        (r'seguridad.*ITAR', "seguridad ITAR"),
        (r'clasificado.*secreto', "clasificado secreto"),
        (r'no.*permite.*subcontrata', "no permite subcontratar")
    ]
    
    for pattern, description in exact_phrases:
        if re.search(pattern, query, re.IGNORECASE):
            logger.info(f"🎯 Detectada query de frase exacta: '{description}'")
            return pattern
    
    return None


def route_query(query: str) -> str:
    """Forzamos GPT-4o para todas las queries de datos (lección del 70% accuracy)."""
    return 'COMPLEX'  # Mantener override hasta validar 100%


def load_metadata_context() -> str:
    """
    Carga el contexto de metadatos desde el caché generado offline.
    ULTRA-RÁPIDO: No lee PDFs, solo un archivo de texto pre-generado.
    """
    if not METADATA_CACHE_PATH.exists():
        logger.warning(f"⚠️ Caché de metadatos no encontrado en {METADATA_CACHE_PATH}")
        logger.warning("Ejecuta: python src/ingest_contracts.py")
        return "No hay información de contratos disponible. Ejecuta src/ingest_contracts.py primero."
    
    try:
        with open(METADATA_CACHE_PATH, "r", encoding="utf-8") as f:
            context = f.read()
        logger.info(f"✅ Contexto de metadatos cargado desde caché ({len(context)} chars)")
        return context
    except Exception as e:
        logger.error(f"Error cargando caché de metadatos: {e}")
        return "Error cargando información de contratos."


def expand_context(chunks: List[Dict]) -> List[Dict]:
    """
    CONTEXT EXPANSION: Recupera chunks adyacentes (anterior/posterior) para más contexto.
    Esto ayuda a capturar información que pueda estar fragmentada entre chunks.
    """
    from src.utils.vectorstore import search
    
    expanded = []
    seen_indices = set()
    
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        archivo = metadata.get("archivo") or metadata.get("source")
        chunk_idx = metadata.get("chunk_index", 0)
        
        # Añadir chunk original
        key = f"{archivo}_{chunk_idx}"
        if key not in seen_indices:
            seen_indices.add(key)
            expanded.append(chunk)
        
        # Intentar recuperar chunk anterior (chunk_index - 1)
        if chunk_idx > 0:
            try:
                prev_results = search(
                    query="",  # No importa, buscaremos por metadata
                    top_k=50,
                    filter_metadata={"archivo": archivo, "chunk_index": chunk_idx - 1}
                )
                if prev_results:
                    prev_chunk = prev_results[0]
                    prev_key = f"{archivo}_{chunk_idx - 1}"
                    if prev_key not in seen_indices:
                        seen_indices.add(prev_key)
                        # Insertar ANTES del chunk actual
                        expanded.insert(len(expanded) - 1, prev_chunk)
            except:
                pass  # Silently fail, no es crítico
        
        # Intentar recuperar chunk posterior (chunk_index + 1)
        try:
            next_results = search(
                query="",
                top_k=50,
                filter_metadata={"archivo": archivo, "chunk_index": chunk_idx + 1}
            )
            if next_results:
                next_chunk = next_results[0]
                next_key = f"{archivo}_{chunk_idx + 1}"
                if next_key not in seen_indices:
                    seen_indices.add(next_key)
                    expanded.append(next_chunk)
        except:
            pass
    
    return expanded if expanded else chunks  # Fallback al original si falla


def format_context_from_chunks(chunks: List[Dict]) -> Tuple[str, Dict[str, str]]:
    """Formatea chunks recuperados como contexto para el LLM con mapeo de fuentes."""
    if not chunks:
        return "No se encontraron documentos relevantes.", {}
    
    context_parts = []
    source_map = {}
    
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        doc_key = f"Documento {i}"
        
        # Nombre real del archivo
        real_name = metadata.get("archivo") or metadata.get("source") or "Desconocido.pdf"
        if not real_name.lower().endswith(".pdf"):
            real_name += ".pdf"
        
        # Página
        page = metadata.get("pagina") or metadata.get("page") or "1"
        
        # Mapeo para post-procesamiento
        source_map[doc_key] = f"{real_name}, Pág: {page}"
        
        # Header del chunk
        header = f"[{doc_key}] (Archivo: {real_name})"
        
        if metadata.get("num_contrato"):
            header += f" Contrato: {metadata['num_contrato']}"
        if metadata.get("seccion"):
            header += f" | Sección: {metadata['seccion']}"
        
        # Contenido limitado
        contenido = chunk['contenido'][:1200] + "..." if len(chunk['contenido']) > 1200 else chunk['contenido']
        context_parts.append(f"{header}\n{contenido}")
    
    return "\n\n---\n\n".join(context_parts), source_map


def extract_dates_from_text(text: str) -> List[str]:
    """Extrae fechas del texto."""
    pattern = r'\d{1,2}/\d{1,2}/\d{4}'
    return re.findall(pattern, text)


def validate_response(response: str, chunks: List[Dict]) -> Tuple[str, List[str]]:
    """Valida respuesta del LLM y detecta posibles problemas."""
    warnings = []
    
    # Verificar citas de contratos
    contract_patterns = [
        r'[A-Z]{2,4}_\d{4}_\d{3}',
        r'EXP[_-]\d{4}[_-]\d+',
        r'CON[_-]\d{4}[_-]\d+',
        r'LIC[_-]\d{4}[_-]\d+'
    ]
    
    has_contract_citation = any(re.search(pattern, response, re.IGNORECASE) for pattern in contract_patterns)
    
    if not has_contract_citation and chunks:
        chunk_contracts = [chunk.get("metadata", {}).get("num_contrato") for chunk in chunks if chunk.get("metadata", {}).get("num_contrato")]
        if chunk_contracts:
            warnings.append("⚠️ Esta respuesta es general. Contratos relacionados: " + ", ".join(set(chunk_contracts)))
    
    # Verificar fechas
    response_dates = extract_dates_from_text(response)
    if response_dates:
        chunk_text = " ".join([c.get("contenido", "") for c in chunks])
        chunk_dates = extract_dates_from_text(chunk_text)
        for date in response_dates:
            if date not in chunk_dates:
                warnings.append(f"⚠️ La fecha {date} no se ha podido verificar en los documentos originales.")
                break
    
    if len(response.strip()) < 50 and chunks:
        warnings.append("💡 Si necesitas más detalle, puedo elaborar la respuesta.")
    
    return response, warnings



def analyze_date_density(initial_chunks: List[Dict]) -> str:
    """
    Realiza un análisis exhaustivo de densidad de fechas para los contratos candidatos.
    Recupera TODOS los chunks de los contratos encontrados y cuenta fechas únicas.
    """
    try:
        # 1. Identificar contratos candidatos de los chunks iniciales
        candidate_contracts = set()
        for chunk in initial_chunks:
            c_id = chunk.get("metadata", {}).get("num_contrato")
            if c_id and c_id != "N/A":
                candidate_contracts.add(c_id)
                
        if not candidate_contracts:
            return ""

        logger.info(f"📅 Analizando densidad para contratos: {candidate_contracts}")
        results = []
        
        # 2. Para cada contrato, recuperar TODOS sus chunks y contar fechas
        from src.utils.vectorstore import get_collection
        from src.utils.deterministic_extractor import extract_dates
        
        collection = get_collection()
        
        for contract_id in candidate_contracts:
            # Recuperar todo el contenido del contrato usando GET directo (sin embedding)
            # Retorna diccionarios con listas: {'ids': [...], 'documents': [...], ...}
            contract_data = collection.get(
                where={"num_contrato": contract_id},
                limit=100,
                include=["documents"]
            )
            
            if not contract_data or not contract_data['documents']:
                continue
                
            all_text = " ".join(contract_data['documents'])
            dates = extract_dates(all_text)
            unique_dates = sorted(list(set(dates)))
            
            results.append({
                "contract": contract_id,
                "count": len(unique_dates),
                "dates": unique_dates
            })
        
        # 3. Ordenar por cantidad
        results.sort(key=lambda x: x["count"], reverse=True)
        
        # 4. Formatear reporte para el LLM
        report = "=== ANÁLISIS DE DENSIDAD DE FECHAS (EDGE_04 FIX) ===\n"
        report += "Este análisis cuenta fechas únicas de TODOS los chunks del contrato, no solo los recuperados.\n"
        for r in results[:3]: # Top 3
            report += f"- Contrato {r['contract']}: {r['count']} fechas únicas encontradas.\n"
            if r['count'] > 0:
                report += f"  (Ejemplos: {', '.join(r['dates'][:5])}...)\n"
            
        return report
    except Exception as e:
        logger.error(f"Error en analyze_date_density: {e}")
        return ""


def format_conversation_history(history: List[Dict], max_messages: int = 5) -> str:
    """Formatea historial de conversación."""
    if not history:
        return ""
    
    recent_history = history[-max_messages:]
    if not recent_history:
        return ""
    
    formatted = ["HISTORIAL DE CONVERSACIÓN RECIENTE:"]
    for msg in recent_history:
        role = "Usuario" if msg.get("role") == "user" else "Asistente"
        content = msg.get("content", "")[:2000]
        formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted)


def contextualize_query(query: str, history: List[Dict]) -> str:
    """Reescribe query basándose en historial para hacerla independiente."""
    if not history:
        return query
    
    try:
        historial_str = format_conversation_history(history, max_messages=3)
        prompt = CONDENSED_QUESTION_PROMPT.format(
            chat_history=historial_str,
            question=query
        )
        
        logger.info("Contextualizando pregunta...")
        response = generate_response(prompt, max_tokens=150, temperature=0.0)
        
        cleaned = response.strip()
        if cleaned.lower().startswith("pregunta independiente:"):
            cleaned = cleaned[23:].strip()
        cleaned = cleaned.replace('"', "").strip()
        
        if not cleaned or "Error" in cleaned:
            return query
        
        return cleaned
    except Exception as e:
        logger.error(f"Error en contextualize_query: {e}")
        return query






def retrieve_and_generate(query: str, history: List[Dict] = None) -> Dict:
    """
    Ejecuta el flujo RAG completo con BÚSQUEDA HÍBRIDA FORZADA.
    
    Args:
        query: Pregunta del usuario.
        history: Historial de conversación (opcional).
    
    Returns:
        Dict: Respuesta con metadatos.
    """
    result = {
        "query": query,
        "response": "",
        "sources": [],
        "warnings": [],
        "success": True
    }
    
    # Clasificar query
    query_type = classify_query(query)
    logger.info(f"Tipo de query: {query_type}")
    
    # Respuestas rápidas
    if query_type == 'GREETING':
        result["response"] = "¡Hola! 👋 Soy DefenseBot, tu asistente para consultas de contratos de defensa. ¿En qué puedo ayudarte hoy?"
        return result
    
    if query_type == 'HELP':
        result["response"] = ("¡Por supuesto! Puedo ayudarte con:\n\n"
                              "• 💰 **Importes y avales** de contratos\n"
                              "• 📅 **Fechas de vencimiento** y plazos\n"
                              "• 🔒 **Clasificaciones de seguridad**\n"
                              "• 📜 **Normas y certificaciones** (STANAG, ISO)\n"
                              "• 🚨 **Penalizaciones** contractuales\n\n"
                              "Prueba preguntas como:\n"
                              "- ¿Cuál es el contrato de mayor importe?\n"
                              "- ¿Qué contratos vencen pronto?\n"
                              "- ¿Qué avales tiene el contrato CON_2024_001?")
        return result
    
    # Validaciones
    if not is_vectorstore_initialized():
        result["response"] = "No hay documentos cargados. Ejecuta: python src/ingest_contracts.py"
        result["success"] = False
        return result
    
    if not is_model_available():
        result["response"] = "El modelo de IA no está disponible."
        result["success"] = False
        return result
    
    try:
        import time
        start_retrieval = time.time()
        
        # ============================================
        # BÚSQUEDA HÍBRIDA FORZADA (BM25 + Vector)
        # ============================================
        logger.info("🔍 Ejecutando BÚSQUEDA HÍBRIDA (BM25 + Vector)...")
        
        # [Fase 2: Smart Routing]
        # Clasificar y obtener configuración
        router = QueryRouter()
        complexity = router.classify(query)
        config = router.get_config(complexity)
        
        logger.info(f"🧠 Smart Routing: Query clasificada como '{complexity}'")
        logger.info(f"⚙️ Configuración: {config}")

        # 1. Ajuste de Top-K basado en Router
        top_k = config["top_k"]

        # [Fase 3: Query Understanding Layer - Compatibility]
        # Mantener QueryAnalyzer para intenciones específicas (como LIST/EXHAUSTIVE/SINGLE_DOC)
        # Si QueryAnalyzer pide más chunks que el Router, respetamos el mayor (safety fallback)
        from src.agents.query_analyzer import QueryAnalyzer
        analyzer = QueryAnalyzer()
        query_plan = analyzer.analyze(query)
        
        if query_plan.get("search_strategy") == "EXHAUSTIVE_SCAN" or query_plan.get("query_type") == "LIST":
             if top_k < 50:
                 top_k = 50
                 logger.info(f"🚀 Override: Modo Exhaustivo Activado (k={top_k}) por Query Plan")
        elif query_plan.get("search_strategy") == "SINGLE_DOC":
             # Si es Single Doc, el Router probablemente ya dijo SIMPLE/MEDIUM (5-15), así que está bien.
             pass

        logger.info(f"📊 Top-K final: {top_k} chunks")
        
        # 2. Extracción de filtros de metadatos del plan
        
        # 2. Extracción de filtros de metadatos del plan
        filter_metadata = None
        plan_contracts = query_plan.get("entities", {}).get("contract_ids", [])
        
        if plan_contracts:
            contract_id = plan_contracts[0] 
            filter_metadata = {"num_contrato": contract_id}
            logger.info(f"🎯 Filtro Metadata Activado (Analyzer): {contract_id}")
        
        # Metadata Filtering ya se determinó arriba con el Query Analyzer
        # Si falló el Analyzer, fallback a extracción regex simple (ya integrado en Analyzer pero por seguridad)
        if not filter_metadata:
             contract_id = extract_contract_id(query)
             if contract_id:
                 filter_metadata = {"num_contrato": contract_id}
                 logger.info(f"🎯 Filtrando por contrato: {contract_id}")
        
        chunks = hybrid_search(query, top_k=top_k, filter_metadata=filter_metadata)
        
        # 3. Smart Re-ranking Depth (Condicional por Router)
        chunks_to_rank = []
        if config["use_reranker"]:
            rerank_limit = top_k # Re-rankeamos todo lo traído si el router dice que es complejo
            
            # Optimización extra si es muy masivo
            if rerank_limit > 30:
                rerank_limit = 30 # Cap safety
                
            chunks_to_rank = chunks[:rerank_limit]
            logger.info(f"🎯 Re-ranking ACTIVADO por Router ({len(chunks_to_rank)} chunks)...")
            
            try:
                chunks = rerank_chunks(query, chunks_to_rank, top_k=min(30, len(chunks_to_rank)))
            except Exception as e:
                logger.error(f"Re-ranking falló: {e}, usando orden original")
                chunks = chunks[:30]
        else:
            logger.info("⏩ Re-ranking DESACTIVADO por Router (Modo Rápido)")
            chunks = chunks[:top_k]
        
        retrieval_time = time.time() - start_retrieval
        logger.info(f"⏱️ Retrieval completado en {retrieval_time:.2f}s - {len(chunks)} chunks")
        
        # Extraer fuentes
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            source = {
                "contrato": meta.get("num_contrato", "N/A"),
                "seccion": meta.get("seccion", "General"),
                "archivo": meta.get("archivo", "N/A")
            }
            if source not in result["sources"]:
                result["sources"].append(source)
        
        # Formatear contexto (SIN context expansion por ahora, tiene bugs)
        if chunks:
            context, source_map = format_context_from_chunks(chunks)
            
            # --- FIX EDGE_04: Análisis de Densidad de Fechas ---
            # Si la query pregunta por densidad o cantidad de fechas, hacemos análisis exhaustivo
            density_keywords = ["densidad", "mayor número de fechas", "más fechas", "más hitos", "cantidad de fechas", "cuántas fechas"]
            if any(k in query.lower() for k in density_keywords):
                logger.info("📅 Detectada query de densidad de fechas. Ejecutando análisis exhaustivo (EDGE_04)...")
                try:
                    density_report = analyze_date_density(chunks)
                    if density_report:
                        context += f"\n\n{density_report}"
                        logger.info("✅ Reporte de densidad inyectado en contexto.")
                except Exception as e:
                    logger.error(f"Error en análisis de densidad: {e}")
            # ---------------------------------------------------
            
        else:
            context = "No se encontraron documentos relevantes."
            source_map = {}
        
        # Generación con LLM
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        historial_str = format_conversation_history(history or [], max_messages=4)
        
        # Determinar modelo (Router Config)
        selected_model = config["model"]
        logger.info(f"🤖 Usando modelo: {selected_model}")
        
        # Paso 1: Extracción Determinista + LLM
        logger.info("Extracción con modo determinista anti-alucinación...")
        
        # PRE-EXTRACCIÓN: Buscar datos específicos con regex
        pre_extracted = {
            "cif": extract_cif(context),
            "fechas": extract_dates(context),
            "importes": extract_amounts(context),
            "normativas": extract_normativas(context),
            "penalizaciones": extract_penalties(context),
            "contrato_mencionado": contract_id
        }
        logger.info(f"Pre-extracción: CIF={pre_extracted['cif']}, Fechas={len(pre_extracted['fechas'])}, Importes={len(pre_extracted['importes'])}")
        
        # PROMPT EXTRACTOR V2: Anti-Alucinación + Determinista
        extractor_v2 = f"""
Actúas como EXTRACTOR DE DATOS ULTRA-PRECISOS de contratos de defensa.

PREGUNTA DEL USUARIO:
{query}

CONTEXTO (Documentos verificados):
{context}

HISTORIAL DE CONVERSACIÓN:
{historial_str}

DATOS PRE-EXTRAÍDOS (Regex):
- CIFs encontrados: {pre_extracted['cif'] or 'NO CONSTA'}
- Fechas encontradas: {', '.join(pre_extracted['fechas'][:5]) if pre_extracted['fechas'] else 'NO CONSTA'}
- Importes encontrados: {', '.join([a['valor'] for a in pre_extracted['importes'][:5]]) if pre_extracted['importes'] else 'NO CONSTA'}
- Normativas encontradas: {', '.join(pre_extracted['normativas'][:5]) if pre_extracted['normativas'] else 'NO CONSTA'}

🚨 REGLAS ANTI-ALUCINACIÓN (CRÍTICO):
1. Si la pregunta pide un CIF → USA SOLO el pre-extraído. Si no hay, responde "NO CONSTA".
2. Si pide fecha final de ejecución → Busca "finalización" o "fecha final". Sino, usa la MÁS TARDÍA de las pre-extraídas.
3. Si pide importe/penalización EXACTA → USA SOLO valores pre-extraídos. NO inventes.
4. Si pide normativa → USA SOLO normativas pre-extraídas. Si pregunta por "la principal", menciona SOLO UNA.
5. Si pide "todos" o "lista" → Extrae TODOS los contratos/datos encontrados.
6. NO añadas información "adicional" no solicitada.
7. Si NO encuentras el dato exacto → Responde "NO CONSTA EN LOS DOCUMENTOS".

RESPUESTA (formato JSON):
{{
    "dato_encontrado": "Valor exacto extraído o 'NO CONSTA'",
    "fuente_exacta": "Nombre del documento y página",
    "nivel_certeza": "ALTO|MEDIO|BAJO",
    "razonamiento": "Breve explicación de cómo encontraste el dato"
}}
"""
        
        datos_extraidos = generate_response(extractor_v2, max_tokens=800, temperature=0.0, model=selected_model)
        
        # Paso 2: Generación final con Verificación
        logger.info("Síntesis final con verificación de perito...")
        
        # PROMPT DE SÍNTESIS RIGUROSA
        synthesis_prompt = f"""
Actúas como PERITO JUDICIAL que redacta un INFORME OFICIAL.

FECHA: {fecha_actual}

DATOS EXTRAÍDOS (ya verificados):
{datos_extraidos}

PREGUNTA ORIGINAL:
{query}

HISTORIAL DE CONVERSACIÓN:
{historial_str}

INSTRUCCIONES DE REDACCIÓN:
1. Si el dato fue encontrado (nivel_certeza ALTO):
   - Presenta en TABLA MARKDOWN: | Concepto | Valor | Fuente Verificada |
   - Usa SOLO datos literales del JSON extraído.
   - Si preguntan SUMA/TOTAL: Calcula y muestra "SUMA TOTAL: [X] EUR".
   
2. Si el dato NO CONSTA:
   - Responde: "El dato solicitado NO CONSTA en los documentos analizados."
   - NO inventes ni aproximes.

3. Si nivel_certeza es MEDIO/BAJO:
   - Indica: "Se encontró información parcial, pero no es 100% concluyente."

4. PROHIBIDO:
   - Añadir información no extraída.
   - Usar "probablemente", "posiblemente".
   - Inventar cifras o fechas.

REDAC<!-- el informe AHORA:
"""
        
        raw_response = generate_response(synthesis_prompt, max_tokens=700, temperature=0.0, model=selected_model)
        
        # Post-procesamiento: Reemplazar [Documento X] con nombres reales
        response = raw_response
        if source_map:
            pattern = re.compile(r"(?:\[?Documento\s*[:\-]?\s*(\d+)\]?)", re.IGNORECASE)
            
            def replacer(match):
                num = match.group(1)
                key = f"Documento {num}"
                real_ref = source_map.get(key)
                if real_ref:
                    return f"**[Doc: {real_ref}]**"
                return match.group(0)
            
            response = pattern.sub(replacer, raw_response)
        
        # [Fase 3.2: Verificador Post-Generación]
        # Cross-Check respuesta vs chunks
        
        final_response = response
        warnings = []



        # Validación básica antigua (mantener por compatibilidad)
        validated_response, old_warnings = validate_response(final_response, chunks)
        warnings.extend(old_warnings)
        
        result["response"] = validated_response
        result["warnings"] = warnings
        
    except Exception as e:
        logger.error(f"Error en RAG: {e}")
        result["response"] = f"Error procesando la consulta: {str(e)}"
        result["success"] = False
    
    return result



def query_stream(query: str, history: List[Dict] = None) -> Iterator[str]:
    """
    Versión streaming del query.
    Yields tokens en tiempo real para UX instantánea.
    Optimizado para TTFT < 2s (Sin Reranking, Single-Step LLM).
    """
    try:
        # 1. Hybrid Search (Rápido, sin Reranker pesado)
        # Optimizamos a top_k=10 para reducir TTFT (Search + Context Upload)
        chunks = hybrid_search(query, top_k=10)
        
        # 2. Build Prompt (Single Step para velocidad)
        if chunks:
            context, source_map = format_context_from_chunks(chunks)
        else:
            context = "No se encontraron documentos relevantes."
            yield "No se encontró información en la base de datos."
            return

        # Prompt estilo 'Perito Judicial' pero directo
        historial_str = format_conversation_history(history or [])
        
        prompt = f"""
Actúas como PERITO JUDICIAL experto en contratos de defensa.
Tu misión es responder a la pregunta usando SOLO la documentación proporcionada.

PREGUNTA: {query}

CONTEXTO:
{context}

HISTORIAL:
{historial_str}

INSTRUCCIONES:
1. Responde SOLO con información verificable en el contexto.
2. Si la respuesta incluye datos (importes, fechas, CIFs), preséntalos en formato TABLA Markdown.
3. Cita las fuentes exactas (ej: [Doc: Nombre_Archivo.pdf]).
4. Si no hay información suficiente, responde "NO CONSTA EN LA DOCUMENTACIÓN".
5. Sé directo y profesional.

RESPUESTA (Streaming):
"""
        
        # 3. Stream generation
        for token in generate_response_stream(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.0
        ):
            yield token
            
    except Exception as e:
        logger.error(f"Error en streaming: {e}")
        yield f"Error generando respuesta: {str(e)}"


def chat(query: str, history: List[Dict] = None) -> str:
    """
    Interfaz simple para el chatbot con memoria de conversación.
    """
    import time
    start_time = time.time()
    
    result = retrieve_and_generate(query, history)
    
    elapsed_time = time.time() - start_time
    logger.info(f"⏱️ TIEMPO TOTAL RESPUESTA: {elapsed_time:.2f}s para query: '{query[:50]}...'")
    
    response = result["response"]
    
    # Warnings solo en log
    if result.get("warnings"):
        for warning in result["warnings"]:
            logger.warning(f"RAG Warning: {warning}")
    
    # Añadir fuentes
    if result.get("sources") and result.get("success"):
        unique_contracts = list(set(
            s["contrato"] for s in result["sources"] 
            if s["contrato"] not in ["N/A", "Todos"]
        ))
        if unique_contracts:
            response += f"\n\n📄 *Fuente: {', '.join(unique_contracts)}*"
    
    return response
