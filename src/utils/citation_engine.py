"""
Motor de citación granular para respuestas del RAG.
Asegura trazabilidad total de cada afirmación crítica.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CitationEngine:
    """Genera y valida citaciones granulares"""
    
    def __init__(self):
        # Patrones de claims que requieren citación OBLIGATORIA
        self.critical_patterns = {
            "importes": r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:€|EUR)",
            "fechas": r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            "cifs": r"\b([A-Z]-?\d{8})\b",
            "normativas": r"((?:ISO|STANAG|MIL-STD|UNE-EN)\s*[\w\-:]+)",
            "contratos": r"([A-Z]{3}_\d{4}_\d{3})",
            "plazos": r"(\d+)\s*días?\s*(?:naturales|hábiles)",
        }
    
    def generate_with_citations(
        self,
        query: str,
        chunks_with_metadata: List[Dict]
    ) -> Dict[str, Any]:
        """
        Genera respuesta con citaciones inline usando LLM
        
        Args:
            query: Pregunta del usuario
            chunks_with_metadata: Lista de chunks con metadata completa
                [{"text": str, "metadata": {"archivo", "pagina", "seccion"}}, ...]
        
        Returns:
            {
                "answer": str (con citaciones),
                "sources": List[Dict],
                "contradictions": List[Dict]
            }
        """
        from src.utils.llm_config import generate_response
        
        logger.info("📚 Generando respuesta con citaciones...")
        
        # Construir prompt especial para citaciones
        prompt = self._build_citation_prompt(query, chunks_with_metadata)
        
        # Generar con LLM
        # Usamos gpt-4o explícitamente para asegurar calidad en seguimiento de instrucciones
        response = generate_response(prompt, model="gpt-4o")
        
        # Post-procesamiento
        processed = self._post_process_citations(response, chunks_with_metadata)
        
        # Detectar contradicciones
        contradictions = self._detect_contradictions(response, chunks_with_metadata)
        
        # Extraer fuentes únicas
        sources = self._extract_unique_sources(response, chunks_with_metadata)
        
        return {
            "answer": processed,
            "sources": sources,
            "contradictions": contradictions
        }
    
    def _build_citation_prompt(self, query: str, chunks: List[Dict]) -> str:
        """Construye prompt que FUERZA citación granular"""
        
        # Formatear chunks con IDs y metadata visible
        formatted_chunks = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            
            # Asegurar fallback para campos de metadata
            archivo = metadata.get('archivo') or metadata.get('source') or 'Unknown'
            pagina = metadata.get('pagina') or metadata.get('page') or 'N/A'
            seccion = metadata.get('seccion') or 'N/A'
            
            formatted_chunks.append(f"""
[CHUNK_{i}]
Documento: {archivo}
Página: {pagina}
Sección: {seccion}
Contenido:
{chunk.get('text', '')}
""")
        
        prompt = f"""
Actúa como un ANALISTA TÉCNICO-LEGAL especializado en documentación contractual.

Tu misión es responder a esta pregunta con MÁXIMA PRECISIÓN Y TRAZABILIDAD:

**PREGUNTA:**
{query}

**DOCUMENTOS FUENTE:**
{chr(10).join(formatted_chunks)}

---

**REGLAS DE CITACIÓN OBLIGATORIAS (0% TOLERANCIA AL INCUMPLIMIENTO):**

1. **CITACIÓN GRANULAR:** CADA cifra, fecha, normativa, o dato técnico DEBE ir seguido INMEDIATAMENTE de su fuente:
   Formato: [Fuente: NOMBRE_ARCHIVO.md, Pág: X, Sección: Y]
   
   Ejemplo CORRECTO:
   "El importe total es 1.234.567,89 EUR [Fuente: CON_2024_012_Centro_Mando_Retamares.md, Pág: 8, Sección: Presupuesto Base]"
   
   Ejemplo INCORRECTO:
   "El importe total es 1.234.567,89 EUR" (SIN citación)

2. **CITAS INLINE (NO al final):** Las citas van DENTRO del texto, NO al final del párrafo.

3. **DETECCIÓN DE CONTRADICCIONES:** Si dos chunks dan información diferente sobre el MISMO concepto:
   - Menciona AMBAS versiones
   - Cita AMBAS fuentes
   - Añade nota de advertencia:
   
   Ejemplo:
   "⚠️ NOTA: Existe discrepancia en [concepto]:
   • Versión A: [dato] [Fuente: DOC1, Pág: X]
   • Versión B: [dato] [Fuente: DOC2, Pág: Y]
   Recomendación: Verificar con [quien corresponda]."

4. **NO INVENTAR:** Si un dato NO está en los chunks, responde:
   "El dato solicitado NO CONSTA en los documentos analizados."

5. **PRECISIÓN NUCLEAR EN NÚMEROS:** 
   - Los números deben ser EXACTOS (incluir céntimos si los hay)
   - Formato IDÉNTICO al del documento fuente

6. **IDENTIFICACIÓN DE CHUNK:** Usa el ID de chunk para localizar la info (ej: NO menciones CHUNK_X en la respuesta final, usa el nombre del archivo real).

---

**FORMATO DE RESPUESTA ESPERADO:**

[Tu respuesta detallada con citaciones inline]

📄 **FUENTES CONSULTADAS:**
- [Listar documentos únicos usados]

---

Procede con la respuesta. Recuerda: 0% tolerancia a claims sin citar.
"""
        
        return prompt
    
    def _post_process_citations(self, response: str, chunks: List[Dict]) -> str:
        """
        Post-procesamiento de citaciones
        
        NOTA: Las advertencias de citación se manejan en Answer Validator.
        Este método solo formatea las citas existentes, no añade warnings.
        """
        # Extraer citaciones existentes para verificación
        citations = re.findall(r'\[Fuente:([^\]]+)\]', response)
        
        logger.info(f"📌 {len(citations)} citaciones encontradas en respuesta")
        
        # ========== ELIMINADO: Validación de claims sin citar ==========
        # El Answer Validator ya maneja esto en la capa de validación
        # No añadimos advertencias redundantes al texto de la respuesta
        
        # Simplemente retornar la respuesta como está
        # (con las citaciones que el LLM ya generó)
        return response
    
    def _find_uncited_claims(self, text: str) -> List[str]:
        """
        Encuentra claims críticos que NO tienen citación
        """
        uncited = []
        
        # Dividir en sentencias
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            # Verificar si contiene dato crítico
            has_critical_data = any(
                re.search(pattern, sentence) 
                for pattern in self.critical_patterns.values()
            )
            
            # Verificar si tiene citación
            has_citation = bool(re.search(r'\[Fuente:', sentence))
            
            if has_critical_data and not has_citation:
                # Extraer el dato específico
                for claim_type, pattern in self.critical_patterns.items():
                    match = re.search(pattern, sentence)
                    if match:
                        uncited.append({
                            "claim": match.group(0),
                            "type": claim_type,
                            "sentence": sentence.strip()
                        })
        
        return uncited
    
    def _detect_contradictions(
        self,
        response: str,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        Detecta contradicciones entre documentos
        
        Busca en la respuesta secciones con "⚠️ NOTA: Existe discrepancia"
        """
        contradictions = []
        
        # Patrón para detectar notas de discrepancia
        discrepancy_pattern = r'⚠️\s*NOTA:\s*Existe discrepancia.*?(?=\n\n|\Z)'
        
        matches = re.findall(discrepancy_pattern, response, re.DOTALL)
        
        for match in matches:
            contradictions.append({
                "text": match,
                "severity": "WARNING",
                "requires_human_review": True
            })
        
        return contradictions
    
    def _extract_unique_sources(
        self,
        response: str,
        chunks: List[Dict]
    ) -> List[Dict]:
        """
        Extrae lista de fuentes únicas citadas
        """
        sources = set()
        
        # Extraer todos los nombres de archivo citados
        citations = re.findall(r'\[Fuente:\s*([^,\]]+)', response)
        
        for citation in citations:
            # Limpiar nombre
            clean_name = citation.strip()
            sources.add(clean_name)
        
        # Enriquecer con metadata si está disponible
        enriched_sources = []
        for source_name in sources:
            # Buscar metadata completa en chunks
            for chunk in chunks:
                meta = chunk.get('metadata', {})
                # Normalizar nombres para comparación (por si acaso viene .md o no)
                chunk_file = meta.get('archivo') or meta.get('source') or ''
                
                if source_name in chunk_file or chunk_file in source_name:
                    enriched_sources.append({
                        "archivo": source_name,
                        "num_contrato": meta.get('num_contrato'),
                        "nivel_seguridad": meta.get('nivel_seguridad')
                    })
                    break
        
        # Si no encontró metadata pero la fuente está, añadir simple
        found_names = {s['archivo'] for s in enriched_sources}
        for source_name in sources:
            if source_name not in found_names:
                enriched_sources.append({"archivo": source_name})
        
        return enriched_sources


# ========== FUNCIÓN HELPER ==========

def generate_cited_answer(query: str, chunks_with_metadata: List[Dict]) -> Dict:
    """
    Wrapper simple para generar respuesta con citaciones
    
    Usage:
        result = generate_cited_answer(query, chunks)
        print(result['answer'])  # Respuesta con citaciones inline
    """
    engine = CitationEngine()
    return engine.generate_with_citations(query, chunks_with_metadata)
