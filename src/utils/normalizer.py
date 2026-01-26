# -*- coding: utf-8 -*-
"""
Normalizador Inteligente de Documentos.
Utiliza GPT-4o para convertir PDFs desestructurados en Markdown estandarizado.
"""

import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
from openai import OpenAI

from src.config import OPENAI_API_KEY, MODEL_NORMALIZER, SECTION_DELIMITER

logger = logging.getLogger(__name__)

NORMALIZER_PROMPT = f"""Eres un EXPERTO EN ESTRUCTURACIÓN DE DOCUMENTOS LEGALES Y DEFENSA.
Tu tarea es leer el texto extraído de un PDF y convertirlo en un documento MARKDOWN PERFECTO.

REGLAS DE ORO:
1. USA EL DELIMITADOR DE SECCIONES: Antes de cada bloque lógico importante de información, añade una línea con "{SECTION_DELIMITER} NOMBRE DE LA SECCIÓN {SECTION_DELIMITER}".
2. PRESERVA TABLAS: Si encuentras datos tabulares, conviértelos a tablas Markdown impecables.
3. LIMPIEZA TOTAL: Elimina números de página sueltos, pies de página repetitivos y ruido de lectura.
4. METADATA AL INICIO: Crea una sección inicial llamada "{SECTION_DELIMITER} METADATA GLOBAL {SECTION_DELIMITER}" con campos como Expediente, Objeto, Importe, Contratista, etc.
5. NO INVENTES: Si algo no está claro, mantén el texto lo más fiel posible pero con formato limpio.

FORMATO DE SALIDA ESPERADO:
{SECTION_DELIMITER} METADATA GLOBAL {SECTION_DELIMITER}
- Expediente: [Valor]
- Contratista: [Valor]
- Importe: [Valor]
...

{SECTION_DELIMITER} OBJETO DEL CONTRATO {SECTION_DELIMITER}
[Contenido...]

{SECTION_DELIMITER} GARANTÍAS {SECTION_DELIMITER}
[Contenido...]

TEXTO DEL DOCUMENTO:
"""

class DocumentNormalizer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        
    def normalize(self, raw_text: str) -> Optional[str]:
        """
        Envía el texto crudo a GPT-4o para normalización.
        """
        if not self.client:
            logger.error("No se ha configurado la API Key de OpenAI")
            return None
            
        try:
            logger.info(f"Normalizando documento con {MODEL_NORMALIZER}...")
            
            response = self.client.chat.completions.create(
                model=MODEL_NORMALIZER,
                messages=[
                    {"role": "system", "content": NORMALIZER_PROMPT},
                    {"role": "user", "content": raw_text}
                ],
                temperature=0
            )
            
            normalized_content = response.choices[0].message.content
            logger.info("Normalización completada satisfactoriamente")
            return normalized_content
            
        except Exception as e:
            logger.error(f"Error en la normalización con OpenAI: {e}")
            return None

def save_normalized_doc(content: str, original_path: Path) -> Path:
    """
    Guarda el contenido normalizado en un archivo .md en la carpeta data/normalized.
    """
    output_dir = original_path.parent.parent / "normalized"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{original_path.stem}_normalized.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return output_path
