# -*- coding: utf-8 -*-
"""
Configuración global del Sistema de Control de Contratos de Defensa.
Lee variables del archivo .env con valores por defecto.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# CONFIGURACIÓN OPENAI (OBLIGATORIO)
# ============================================
# Lee de .env o de variables de entorno del sistema
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Modelos OpenAI
MODEL_NORMALIZER = os.getenv("MODEL_NORMALIZER", "gpt-4o")
MODEL_CHATBOT = os.getenv("MODEL_CHATBOT", "gpt-4o")  # Upgraded from gpt-4o-mini for precision
MODEL_EMBEDDINGS = os.getenv("MODEL_EMBEDDINGS", "text-embedding-3-large")

# ============================================
# CONFIGURACIÓN DE CHROMADB
# ============================================
VECTORSTORE_PATH = os.getenv("VECTORSTORE_PATH", str(BASE_DIR / "data" / "vectorstore"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "contratos_defensa")

# Dimensiones de embeddings según modelo
EMBEDDING_DIMENSIONS = 3072  # text-embedding-3-large

# ============================================
# CONFIGURACIÓN DE EMAIL (Gmail SMTP)
# ============================================
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
DEFAULT_RECIPIENT = os.getenv("DEFAULT_RECIPIENT", "admin@defensa.es")

# ============================================
# RUTAS DE LA APLICACIÓN
# ============================================
CONTRACTS_PATH = Path(os.getenv("CONTRACTS_PATH", str(BASE_DIR / "data" / "contracts")))
NORMALIZED_PATH = BASE_DIR / "data" / "normalized"  # Documentos normalizados con GPT-4o
LOGS_PATH = Path(os.getenv("LOGS_PATH", str(BASE_DIR / "data" / "logs")))
LOGS_FILE = LOGS_PATH / "app.log"

# ============================================
# CONFIGURACIÓN DE ALERTAS
# ============================================
ALERT_DAYS_HIGH = 15      # Días para prioridad ALTA
ALERT_DAYS_MEDIUM = 30    # Días para prioridad MEDIA
ALERT_DAYS_MILESTONE = 15 # Días para alertas de hitos

# ============================================
# CONFIGURACIÓN DE CHUNKING
# ============================================
CHUNK_MAX_TOKENS = 1000   # Máximo tokens por chunk
CHUNK_OVERLAP = 100       # Overlap entre chunks
SECTION_DELIMITER = "───" # Delimitador de secciones en PDFs

# ============================================
# PROMPTS PARA CADENA OPENAI (2 pasos)
# ============================================

# PASO 1: Extractor - extrae datos relevantes de los chunks
EXTRACTOR_PROMPT = """Eres un INVESTIGADOR DE DATOS DEFENSA. Tu misión es encontrar TODA la información relevante en los documentos.

HISTORIAL DE CONVERSACIÓN:
{historial}

PREGUNTA PRIORITARIA: {pregunta}

DOCUMENTACIÓN (FRAGMENTOS):
{contexto}

TAREA DE EXTRACCIÓN:
Analiza los fragmentos y el historial para extraer CUALQUIER dato que ayude a responder.
Si la pregunta hace referencia a "los anteriores", usa el historial para identificar contexto.

Busca activamente:
- Nombres de entidades (Bancos, Empresas)
- Importes (Euros, Cifras)
- Fechas (Vencimientos, Firmas)
- Números de Contrato (CON_..., EXP_...)

FORMATO DE SALIDA (Para cada hallazgo):
- HALLAZGO: [Descripción breve del dato encontrado]
- FUENTE: [Archivo o contrato donde aparece]
- CONFIANZA: [Alta/Media/Baja]

Si la pregunta es sobre avales, busca términos como "Aval", "Garantía", "Caución", "Línea de riesgo".
Si la pregunta es sobre importes, busca "Presupuesto", "Adjudicación", "Valor estimado".

NO INVENTES NADA, pero NO FILTRES información que podría ser útil.
DATOS EXTRAÍDOS:"""

# PASO 2: Respondedor - genera respuesta perfecta con datos extraídos
RESPONDER_PROMPT = """Eres DefenseBot, el asistente de inteligencia de COHEMO.

FECHA ACTUAL: {fecha_actual}

HISTORIAL RECIENTE:
{historial}

PREGUNTA DEL USUARIO: {pregunta}

EVIDENCIA RECOLECTADA POR EL ANALISTA:
{datos_extraidos}

TU OBJETIVO:
Responder a la pregunta del usuario utilizando la evidencia recolectada.
- Si encontraste datos concretos, preséntalos en una lista clara o tabla markdown.
- Si los datos son parciales, presenta lo que tengas y aclara que es información parcial.
- Utiliza negritas para resaltar importes y nombres clave.
- Sé profesional, directo y utiliza lenguaje militar/corporativo ("Se ha identificado", "Informe de situación").

Si la evidencia dice "Banco Santander" y un importe, RELACIONALOS.
No digas "No se encontró información" si hay evidencia clara en el reporte del analista.

RESPUESTA:"""

# PASO 0: Contextualizador - reescribe preguntas de seguimiento
CONDENSED_QUESTION_PROMPT = """Dada la siguiente conversación y una pregunta de seguimiento, refrasea la pregunta de seguimiento para que sea una pregunta independiente que capture todo el contexto necesario.
Si la pregunta ya es independiente y no depende del historial, devuélvela tal cual.
NO respondas a la pregunta, solo reescríbela para que sea clara para un buscador.

HISTORIAL DE CONVERSACIÓN:
{chat_history}

PREGUNTA DE SEGUIMIENTO: {question}

PREGUNTA INDEPENDIENTE:"""


# ============================================
# CREACIÓN DE DIRECTORIOS
# ============================================
def ensure_directories():
    """Crea los directorios necesarios si no existen."""
    CONTRACTS_PATH.mkdir(parents=True, exist_ok=True)
    LOGS_PATH.mkdir(parents=True, exist_ok=True)
    Path(VECTORSTORE_PATH).mkdir(parents=True, exist_ok=True)

# Ejecutar al importar
ensure_directories()
