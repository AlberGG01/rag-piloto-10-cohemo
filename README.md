
# 🛡️ DefenseRAG v2.1.0 (Release Candidate)

> **Sistema de Inteligencia Artificial para el Análisis de Contratos de Defensa**
> *Generación Aumentada por Recuperación (RAG) con Agentes Cognitivos*

![Status](https://img.shields.io/badge/Status-Certified-success)
![Accuracy](https://img.shields.io/badge/Accuracy-86.7%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

## 📖 Descripción
DefenseRAG es un sistema avanzado de **RAG Agéntico** diseñado para auditar, interrogar y extraer inteligencia de documentos de contratación pública militar. A diferencia de los sistemas RAG tradicionales, utiliza una arquitectura de **"Planificación y Descomposición"** para resolver consultas complejas que requieren:

*   **Agregación de datos** (Suma de importes, conteo de contratos).
*   **Comparativas** (Diferencias de plazos, penalizaciones).
*   **Razonamiento Multi-hop** (Conexión de cláusulas entre documentos).

## 🚀 Métricas de Certificación (Hard Mode)
El sistema ha sido auditado con un **Golden Dataset de 30 preguntas complejas**, superando los estándares de producción.

| Métrica | Resultado | Objetivo | Estado |
| :--- | :--- | :--- | :--- |
| **Exactitud (Accuracy)** | **86.7%** | > 85% | ✅ CERTIFICADO |
| **Recall (Recuperación)** | **92.0%** | > 90% | ✅ CERTIFICADO |
| **Calidad de Respuesta** | **4.23 / 5** | > 4.0 | ✅ CERTIFICADO |
| **Velocidad Media** | **58s** | - | ⚡ OPTIMIZADO |

*Certificación emitida el 27/01/2026. Ver [Evaluation Report](evaluation_report.md).*

---

## 🏗️ Arquitectura Técnica "Divide & Conquer"
El sistema implementa una estrategia de descomposición cognitiva:

1.  **Planner Agent**: Analiza la pregunta y detecta si implica múltiples entidades.
2.  **Decomposer**: Rompe preguntas complejas (ej: *"Suma los importes de X e Y"*) en sub-queries atómicas (*"Importe X"*, *"Importe Y"*).
3.  **Parallel Retrieval**: Ejecuta búsquedas vectoriales independientes para cada sub-query.
4.  **Refina & Sintetiza**: Un reranker (BGE-M3) filtra el ruido y el Agente de Síntesis (GPT-4o) construye la respuesta final con citas exactas.


## 🌟 Funcionalidades Avanzadas (v5.2)

### 🧠 Memoria Contextual (Chat)
*   **Sliding Window**: Mantiene un historial de los últimos 5 mensajes para entender referencias como *"¿Cuál es su importe?"* sin repetir el nombre del contrato.
*   **State Isolation**: Gestión de estado segura por `thread_id`.

### 🛡️ Integrity Supervisor & Self-Healing
Un pipeline de ingesta robusto que garantiza "Calidad 10/10" antes de indexar:
1.  **Auditoría Estructural**: Detecta tablas rotas y OCR defectuoso.
2.  **Reparación Automática**: El `RepairAgent` corrige la sintaxis Markdown sin alucinar datos.
3.  **Data Safety Belt**: Verifica que la reparación no alteró ni un solo dígito con respecto al original (protección contra fraude numérico).

### 👮 Clasificación de Seguridad
Clasificación automática de documentos en 4 niveles basada en contenido:
*   **Nivel 1 (Público)**: Manuales.
*   **Nivel 2 (Interno)**.
*   **Nivel 3 (Confidencial)**: Contratos estándar y financieros.
*   **Nivel 4 (Restringido)**: Inteligencia y Estrategia Militar.

### 🚦 Panel de Auditoría HITL
Interfaz Streamlit dedicada (`src/ui/audit_panel.py`) para revisar documentos bloqueados.

---


## 🛠️ Instalación y Uso

### Prerrequisitos
*   Python 3.10+
*   Clave API de OpenAI

### 1. Clonar e Instalar
```bash
git clone https://github.com/organization/defense-rag.git
cd defense-rag
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
```

### 2. Configuración
Crea un archivo `.env` en la raíz:
```ini
OPENAI_API_KEY=sk-tu-clave-aqui
VECTORSTORE_PATH=data/vectorstore
```

### 3. Ejecutar Demo
El sistema viene con datos sintéticos precargados en `data/pdfs`.
```bash
# Iniciar interfaz de chat
streamlit run src/interface/streamlit_app.py
```

### 4. Reproducir Certificación
Para verificar las métricas de precisión:
```bash
python scripts/evaluate_hard_mode.py
```

---

## 📂 Estructura del Proyecto
```
defense-rag/
├── data/               # Documentos PDF y Vectorstore ChromaDB
├── docs/               # Documentación de Arquitectura y Reportes
├── scripts/            # Scripts de Evaluación y Mantenimiento
├── src/
│   ├── agents/         # Lógica de Agentes (Planner, RAG, Synthesis)
│   ├── graph/          # Estados de LangGraph
│   └── utils/          # Herramientas (Vectorstore, Reranker)
├── tests/              # Golden Datasets
└── requirements.txt    # Dependencias
```

## 🔒 Auditoría de Seguridad
*   **Sin Hardcoded Secrets**: Gestión estricta vía variables de entorno.
*   **Datos Sintéticos**: Toda la información contenida en `data/` es ficticia y segura para distribución pública.

---
**© 2026 Defense AI Team.** *Proyecto de Código Abierto para Auditoría de Defensa.*
