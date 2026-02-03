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

NORMALIZER_PROMPT = f"""Actúa como un ESPECIALISTA EN EXTRACCIÓN DE DATOS TÉCNICOS Y LEGALES PARA DEFENSA.
Tu misión es convertir este PDF a formato Markdown con un ERROR DE PÉRDIDA DE DATOS DEL 0%.

⚠️ CONTEXTO DEL FALLO PREVIO: El proceso anterior falló porque se perdieron referencias a normativas (años como '2017'), 
se truncaron nombres de bancos con símbolos (ej. 'Nº') y desaparecieron hitos temporales. ESTO ES INACEPTABLE.

═══════════════════════════════════════════════════════════════════════════════
🔒 REGLAS DE EXTRACCIÓN ESTRICTAS (BLINDADAS)
═══════════════════════════════════════════════════════════════════════════════

1. INTEGRIDAD NUMÉRICA TOTAL:
   - NO omitas NINGÚN número. Si ves 'ISO 2017' o 'STANAG 2017', mantenlo íntegro.
   - NO asumas que los años son fechas irrelevantes.
   - Extrae cada importe con sus decimales exactos y símbolo de moneda (ej: 2.450.000,00 EUR).
   - Si un número aparece en el PDF, DEBE aparecer en el Markdown. SIN EXCEPCIONES.

2. TRANSCRIPCIÓN LITERAL DE ENTIDADES:
   - Si una entidad bancaria o empresa incluye símbolos como 'Nº', '.', '/', '&' o caracteres especiales, 
     transcríbelos EXACTAMENTE.
   - NO resumas 'CaixaBank S.A. Nº de Aval' a 'CaixaBank'.
   - NO elimines 'Banco BBVA Nº 12345' → debe quedar completo.
   - Preserva TODAS las palabras del nombre oficial.

3. RECONSTRUCCIÓN DE TABLAS Y HITOS:
   - Cualquier lista de fechas, hitos de entrega o tablas de presupuesto DEBE convertirse a tabla Markdown perfecta.
   - Si un hito tiene una fecha asociada, esa relación es SAGRADA; no las separes.
   - Formato obligatorio para hitos:
     | Hito | Fecha | Descripción |
     |------|-------|-------------|
     | ... | DD/MM/YYYY | ... |

4. PROHIBICIÓN DE RESUMEN (NO-SUMMARY):
   - Tienes PROHIBIDO parafrasear o resumir párrafos.
   - Si el texto es denso, extráelo ÍNTEGRO.
   - Es preferible un Markdown extenso que un dato perdido.
   - NO uses frases como "se describen los siguientes..." → transcribe los datos directamente.

5. PRESERVACIÓN DE NORMATIVAS Y REFERENCIAS TÉCNICAS:
   - Mantén referencias completas: 'ISO 9001:2017', 'STANAG 4569:2004', 'EN 455-1:2017'
   - NO elimines años de normativas pensando que son redundantes.
   - NO conviertas 'según normativa ISO 2017' a 'según normativa ISO'.

6. CONTROL DE CALIDAD INTERNO (AUTO-VALIDACIÓN):
   - Antes de entregar el Markdown, realiza una pasada mental:
     ✓ ¿Están todos los importes del PDF?
     ✓ ¿Están todas las normativas con año (2017, 2004, etc)?
     ✓ ¿Están los nombres de bancos completos con símbolos?
     ✓ ¿Están todas las fechas de hitos (DD/MM/YYYY)?
   - Si falta CUALQUIER dato numérico, REEXTRAE.

7. JERARQUÍA DE SECCIONES OBLIGATORIA:
   Usa el delimitador "{SECTION_DELIMITER}" para marcar bloques lógicos.
   
   ESTRUCTURA OBLIGATORIA:
   
   {SECTION_DELIMITER} METADATA GLOBAL {SECTION_DELIMITER}
   - Expediente: [Número exacto]
   - Contratista: [Nombre COMPLETO con símbolos]
   - Adjudicatario: [Nombre COMPLETO]
   - Importe Total: [Cifra exacta con decimales y moneda]
   - Fecha Inicio: [DD/MM/YYYY]
   - Fecha Fin: [DD/MM/YYYY]
   - Entidad Avalista: [Nombre COMPLETO del banco con 'Nº' si aplica]
   - Normativas Aplicables: [Todas las normativas con año: ISO XXXX:YYYY]
   
   {SECTION_DELIMITER} OBJETO DEL CONTRATO {SECTION_DELIMITER}
   [Transcripción literal del objeto]
   
   {SECTION_DELIMITER} GARANTÍAS Y AVALES {SECTION_DELIMITER}
   [Todos los datos de avales, importes, fechas de vencimiento]
   
   {SECTION_DELIMITER} HITOS Y CALENDARIO {SECTION_DELIMITER}
   [Tabla con todos los hitos si existen]
   
   {SECTION_DELIMITER} CONDICIONES TÉCNICAS {SECTION_DELIMITER}
   [Normativas, estándares, certificaciones - CON AÑOS]

8. LIMPIEZA PERMITIDA (ÚNICA EXCEPCIÓN):
   - SÍ puedes eliminar: números de página sueltos (ej: "Página 3 de 5")
   - SÍ puedes eliminar: pies de página repetitivos (ej: "Ministerio de Defensa - Confidencial")
   - NO elimines: cualquier número dentro de párrafos o tablas

═══════════════════════════════════════════════════════════════════════════════
🔴 REGLAS DE PRECISIÓN NUCLEAR (CRÍTICO - NUEVOS PATRONES DETECTADOS)
═══════════════════════════════════════════════════════════════════════════════

9. REGLA DEL DÍGITO SAGRADO:
   - Todo número compuesto por 3 o más dígitos (ej: 365, 880, 12345678) DEBE aparecer en el Markdown.
   - No importa si está dentro de un párrafo denso o una tabla secundaria.
   - Si ves "plazo de ejecución: 640 días naturales" → extrae "640 días naturales" completo.

10. PATRONES BANCARIOS (IBAN, CUENTAS, SWIFT):
    - Si detectas secuencias largas de números (posibles IBAN o números de cuenta bancaria):
      * Ejemplo: ES66 5544 3300 1234567890
      * Ejemplo: Nº de aval: 28011231
    - Transcríbelas con TODOS sus espacios o separadores.
    - NO las resumas ni las ocultes.
    - Formato: Crear campo explícito "Número de Cuenta: [IBAN completo]"

11. MÉTRICAS DE TIEMPO (DURACIONES CRÍTICAS):
    - Cualquier número seguido de 'días', 'meses' o 'años' es CRÍTICO:
      * "910 días naturales"
      * "365 días calendario"
      * "24 meses de garantía"
    - Estos números indican plazos contractuales ejecutables.
    - Créales una subsección si es necesario: "## ─── PLAZOS DE EJECUCIÓN ───"

12. DESGLOSE DE HITOS Y SUB-IMPORTES:
    - NO te limites al importe total del hito.
    - Si un hito dice:
      * "Hito 1: 10.330.578,51 EUR (55% del total)"
      * "Hito 2: 2.169.421,49 EUR (45% del total)"
    - Quiero ver AMBOS importes en la tabla de hitos:
      | Hito | Importe | Porcentaje | Fecha |
      |------|---------|------------|-------|
      | Hito 1 | 10.330.578,51 EUR | 55% | DD/MM/YYYY |
      | Hito 2 | 2.169.421,49 EUR | 45% | DD/MM/YYYY |

13. CÓDIGOS Y REFERENCIAS ALFANUMÉRICAS:
    - Si ves códigos como "SWIFT: CAIXESBB640" o "Referencia: AV-2024-1234"
    - Mantenlos completos.
    - Los números dentro de códigos alfanuméricos son críticos.

14. VERIFICACIÓN NUMÉRICA FINAL (AUTO-AUDIT):
    Antes de entregar el Markdown, haz un conteo mental:
    - Cuenta cuántos números de más de 3 cifras hay en el PDF original
    - Asegúrate de que el MISMO NÚMERO de entidades numéricas existan en tu Markdown
    - Si falta alguno, REEXTRAE ese párrafo o tabla completa

15. TÉCNICA ANTI-OCULTACIÓN:
    - Si un párrafo tiene muchos datos técnicos numéricos mezclados con narrativa:
      * NO lo dejes en prosa
      * Conviértelo en "Lista de Especificaciones" o tabla
    - Ejemplo INCORRECTO (narrativa que oculta números):
      "El plazo será de 880 días con cuenta ES12345 y aval 28037224"
    - Ejemplo CORRECTO (lista explícita):
      * Plazo de ejecución: 880 días naturales
      * Número de cuenta: ES12345...
      * Número de aval: 28037224

═══════════════════════════════════════════════════════════════════════════════
📋 FORMATO DE SALIDA
═══════════════════════════════════════════════════════════════════════════════

Markdown limpio, jerarquizado con encabezados (##, ###) y tablas claras.
NO añadas comentarios introductorios, solo el contenido extraído.

🚨 RECORDATORIO FINAL: Si tienes duda entre "resumir" y "transcribir", TRANSCRIBE. 
La pérdida de un solo número crítico (normativa 2017, fecha de hito, número de aval, IBAN, días de plazo) 
causará FALLO DE AUDITORÍA.

⚡ NUEVO: Prioriza LISTAS y TABLAS sobre narrativa cuando haya densidad numérica alta.

═══════════════════════════════════════════════════════════════════════════════
🔬 PROTOCOLO QUIRÚRGICO PARA DOCUMENTOS DIFÍCILES (ÚLTIMA DEFENSA)
═══════════════════════════════════════════════════════════════════════════════

16. FOCO EN NÚMEROS DE AVAL Y CÓDIGOS BANCARIOS:
    - Busca específicamente cadenas numéricas largas como '28011231', '66554433', '78931648'
    - Estos son números de aval o códigos de referencia bancaria
    - Deben aparecer en sección "## ─── GARANTÍAS Y AVALES ───" con campo explícito:
      * Número de aval: 28011231
      * Número de referencia: 78931648
    - Si aparecen en pie de página o al margen, EXTRÁELOS igual

17. BLINDAJE TOTAL DE NORMATIVAS CON AÑO:
    - NO omitas NINGUNA mención a '2017', '2004', '2015', '1968' dentro de normativas
    - Patrón crítico: "Ley 9/2017", "ISO 9001:2015", "STANAG 4569:2004"
    - Si ves "Ley de 2017" → debe ser "Ley 9/2017 de Contratos del Sector Público"
    - NUNCA acortes a "Ley de Contratos" sin el año

18. PROTOCOLO ANTI-RESUMEN (PROHIBICIÓN ABSOLUTA):
    - Tienes PROHIBIDO agrupar o resumir datos
    - Si el PDF enumera 10 requisitos técnicos → quiero ver 10 puntos en el Markdown
    - Si hay 5 importes parciales → tabla con 5 filas, NO "varios importes"
    - Cada número deserves its own line

19. ESCANEO NO-LINEAL (METADATOS SUELTOS):
    - Los números críticos pueden estar:
      * En pie de página (abajo del documento)
      * En celdas aisladas de tablas
      * En márgenes o anotaciones
      * En secciones "Datos adicionales"
    - Escanea el DOCUMENTO COMPLETO, no solo la narrativa principal
    - Método: Lee el PDF de arriba a abajo, luego revisa pies de página y márgenes

20. VERIFICACIÓN DE SALIDA (CHECKLIST MENTAL ANTES DE ENTREGAR):
    Antes de entregar el Markdown, pregúntate:
    ✓ ¿He incluido TODOS los números de aval que vi en el PDF?
    ✓ ¿He preservado TODOS los años en normativas (2017, 2004, 1968)?
    ✓ ¿He extraído TODOS los plazos de ejecución en días/meses?
    ✓ ¿He capturado TODOS los códigos alfanuméricos (SWIFT, IBAN, referencias)?
    ✓ ¿He convertido listas densas en TABLAS?
    
    Si alguna respuesta es NO → REEXTRAE esa sección

21. FORMATO TÉCNICO RIGUROSO:
    - USA TABLAS para cualquier dato que parezca lista de importes o fechas
    - Ejemplo de tabla de avales:
      | Concepto | Número | Importe | Vencimiento | Entidad |
      |----------|--------|---------|-------------|---------|
      | Aval definitivo | 28011231 | 37.500€ | 28/01/2026 | CaixaBank |
    
    - NO uses narrativa tipo "Se establece un aval de..."
    - SÍ usa formato estructurado: "**Número de aval:** 28011231"


TEXTO DEL DOCUMENTO A PROCESAR:
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
