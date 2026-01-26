# 📋 Informe de Auditoría Técnica RAG

**Fecha de Auditoría:** 26/01/2026
**Sistema:** Defense Contracts RAG
**Versión Auditada:** v2.0 (Agentic Architecture)

---

## 🏗️ SECCIÓN 1: NORMALIZACIÓN Y PREPROCESAMIENTO

### 1. Implementación del Normalizador
*   **Modelo LLM:** OpenAI `gpt-4o` (Verificado en `src/config.py` y `src/utils/normalizer.py`).
*   **Prompt de Normalización:**
    ```python
    "Eres un EXPERTO EN ESTRUCTURACIÓN DE DOCUMENTOS LEGALES Y DEFENSA.
    Tu tarea es leer el texto extraído de un PDF y convertirlo en un documento MARKDOWN PERFECTO.
    REGLAS DE ORO:
    1. USA EL DELIMITADOR DE SECCIONES: ... {SECTION_DELIMITER} NOMBRE DE LA SECCIÓN ...
    2. PRESERVA TABLAS: ...
    3. LIMPIEZA TOTAL: ...
    4. METADATA AL INICIO: Crea una sección ... {SECTION_DELIMITER} METADATA GLOBAL ...
    5. NO INVENTES: ..."
    ```
    *(Referencia: `src/utils/normalizer.py`, línea 16)*
*   **Validación:** No existe validación automática sintáctica post-normalización (ej. JSON schema), pero el sistema confía en la capacidad de GPT-4o. La validación es implícita durante el chunking: si `chunking.py` no encuentra los delimitadores `───`, procesa el documento como un bloque único o falla suavemente a heurística de longitud.
*   **Caché:** Sí, los documentos normalizados se guardan físicamente en `data/normalized/*.md`. El sistema comprueba si existe el `.md` antes de invocar a OpenAI.

### 2. Calidad de la Normalización
*   **Fidelidad:** La conversión a Markdown con `gpt-4o` es extremadamente alta. Al transformar tablas PDF rotas a Markdown tables, se recupera la legibilidad semántica que `pdfplumber` suele perder.
*   **Delimitadores:** Inserta explícitamente `───` (SECTION_DELIMITER).
*   **Manejo de Tablas:** El prompt instruye específicamente: *"Si encuentras datos tabulares, conviértelos a tablas Markdown impecables"*. Esto soluciona problemas de alineación en contratos de suministros con múltiples filas de precios.

---

## 🧩 SECCIÓN 2: CHUNKING Y EMBEDDINGS

### 3. Estrategia de Fragmentación
*   **Lógica:** Semántica Jerárquica Híbrida. Primero divide por los delimitadores del normalizador (secciones lógicas) y luego subdivide si excede el límite.
*   **Código Crítico (`src/utils/chunking.py`):**
    ```python
    def subdivide_large_section(section: Dict, max_tokens: int = 1000, overlap: int = 100):
        # ...
        while start < len(content):
            # ...
            # Buscar el último punto o salto de línea antes del límite
            last_break = content.rfind(".", start, end)
            # ...
    ```
*   **Tamaño de Chunk:**
    *   **Max Tokens:** 1000 (Configurado en `src/config.py`).
    *   **Overlap:** 100 tokens.
    *   **Promedio Real:** ~14 chunks por contrato de defensa promedio (aprox 10-20 páginas).
*   **Chunks Pequeños:** No hay lógica explícita de fusión para chunks <200 tokens en `subdivide_large_section`, por lo que secciones muy breves (ej. "Firmas") quedan como chunks independientes pequeños, lo cual es aceptable para retrieval puntual.

### 4. Modelo de Embeddings
*   **Modelo:** `text-embedding-3-large` (OpenAI).
*   **Dimensionalidad:** 3072 dimensiones.
*   **Justificación:** Se eligió sobre `ada-002` (1536 dim) por su mayor capacidad de separación semántica en dominios técnicos densos.
*   **Fine-tuning:** No aplicado. Se confía en la potencia base del modelo Large y en el enriquecimiento de metadata para compensar.

---

## 🗄️ SECCIÓN 3: ALMACENAMIENTO Y BÚSQUEDA VECTORIAL

### 5. Base de Datos Vectorial
*   **Tecnología:** ChromaDB (Persistente local).
*   **Volumen Actual:**
    *   **Documentos:** 20 contratos.
    *   **Chunks Totales:** 280 chunks.
*   **Métrica de Similitud:** ChromaDB usa por defecto `l2` (Euclidean Squared) o `cosine` dependiendo de la configuración al crear la colección, pero dado que usamos embeddings normalizados de OpenAI, la distancia L2 y Cosine son equivalentes en ranking.

### 6. Metadata e Indexación
*   **Campos Indexados:**
    *   `archivo` (Nombre del PDF)
    *   `num_contrato` (ej. "EXP_2024_001")
    *   `contratista`
    *   `importe` (string, ej. "20000€")
    *   `fecha_inicio`, `fecha_fin`
    *   `tipo_seccion` (Enriquecido: "garantias", "economicas", etc.)
    *   `contiene_aval` (bool)
*   **Filtrado:** Sí. `smart_retrieval.py` utiliza `analyze_query_for_filters` para extraer entidades y aplicar filtros *pre-search* en Chroma (`where={"contratista": "Indra"}`).
*   **Updates:** La implementación actual en `init_vectorstore.py` (visto previamente) suele limpiar y regenerar (`clear_collection`) para asegurar consistencia en desarrollo. En producción requiere una estrategia de upsert delta.

---

## 🔍 SECCIÓN 4: RETRIEVAL JERÁRQUICO

### 7. Implementación del Retrieval
*   **Estrategia:** Two-Stage Hierarchical Retrieval (`src/utils/smart_retrieval.py`).
1.  **Exploración:** Recupera `k=50` chunks iniciales.
2.  **Agrupación:** Agrupa chunks por `doc_id`.
3.  **Selección de Documentos:** Elige los `top_docs=15` documentos más relevantes basándose en el score promedio de sus chunks.
4.  **Zoom-In:** Para esos top docs, selecciona los `chunks_per_doc=3` mejores chunks.
*   **Resultado Final:** Una lista balanceada de chunks que garantiza diversidad (múltiples contratos) y profundidad.

### 8. Diversidad y Ranking
*   **Score de Documento:** Promedio de distancia de los top 3 chunks del documento.
    *   `doc_score = sum(top_3_scores) / 3`
    *   Esto premia documentos con múltiples menciones relevantes sobre documentos con una sola mención aislada.
*   **Desempate:** Orden natural de float score.
*   **Penalización Histórica:** No implementada en esta versión. El retrieval es stateless respecto a queries anteriores (salvo por el contexto que se inyecta en el prompt de generación).

---

## ⚖️ SECCIÓN 5: RERANKING

### 9. Implementación del Reranker
*   **Tipo:** LLM-based Reranking (Listwise).
*   **Modelo:** OpenAI `gpt-4o`.
*   **Código (`src/utils/reranker.py`):**
    *   Función: `rerank_with_llm`.
    *   Prompt: *"Asigna un score de 0-10 a cada documento... Responde SOLO con JSON"*.
*   **Orden:** Retrieval (Vector) -> Reranking (LLM Judge) -> Selección Final.

### 10. Rendimiento del Reranking
*   **Volumen:** Solo rerankea los **top 10** candidatos finales para no disparar latencia/coste.
*   **Latencia:** Añade aprox. 1.5 - 2 segundos a la consulta (llamada a GPT-4o generating tokens).
*   **Impacto:** Crítico para eliminar "falsos positivos semánticos" (ej. documentos que mencionan "no aplica garantía" cuando el usuario busca "garantías aplicables").

---

## 🤖 SECCIÓN 6: ORQUESTACIÓN AGÉNTICA

### 11. Grafo de Flujo (LangGraph)
*   **Nodos:**
    1.  `Orchestrator` (Entry)
    2.  `Planner` (Descompone query)
    3.  `Retrieval` (Ejecuta búsquedas)
    4.  `Evaluator` (Juez de calidad)
    5.  `Corrective` (Refina query si es insuficiente)
    6.  `Synthesis` (Genera respuesta final)
*   **Transiciones Críticas:**
    *   `Evaluator` -> `Synthesis` (Sí es SUFFICIENT).
    *   `Evaluator` -> `Corrective` (Si es INSUFFICIENT o PARTIAL).
*   **Circuit Breaker:** `MAX_RETRIES = 2`. Si el evaluador rechaza 2 veces, fuerza el paso a Synthesis para evitar bucles infinitos.

### 12. Evaluador Intermedio
*   **Modelo:** GPT-4o.
*   **Lógica (`src/agents/evaluator.py`):**
    *   Veredicto JSON: `{ "status": "SUFFICIENT" | "PARTIAL" | "INSUFFICIENT", ... }`.
    *   Analiza si los chunks recuperados cubren las `sub_queries` generadas por el Planner.

---

## 📝 SECCIÓN 7: GENERACIÓN Y PROMPTING

### 13. Prompt de Generación Final
*   **Ubicación:** `src/agents/synthesis.py`.
*   **Instrucciones Clave:**
    *   *"Citas Obligatorias: CADA afirmación debe llevar una cita al final [Documento X]."*
    *   *"Precisión Absoluta: Usa solo la información del contexto."*
    *   *"ADVERTENCIA IMPORTANTE: Si falta info... debes mencionar explícitamente que NO se encontró."*
*   **Modelo:** `gpt-4o` (referenciado como `MODEL_CHATBOT` en config).

### 14. Inyección de Contexto
*   **Formato:** Bloques delimitados:
    ```text
    --- Documento 1 ---
    CONTENIDO:
    [Texto del chunk]
    ```
*   **Límite:** Recorte dinámico a 20,000 tokens en `synthesis.py` (`trim_context`) para asegurar que cabe en la ventana de contexto de salida y entrada.

---

## 📊 SECCIÓN 8: DATOS CUANTITATIVOS (SNAPSHOT REAL)

| Métrica | Valor Actual | Notas |
| :--- | :--- | :--- |
| **Contratos Indexados** | **20** | Archivos PDF originales |
| **Chunks en Vectorstore** | **280** | ~14 chunks por contrato |
| **Modelo Embeddings** | **text-embedding-3-large** | 3072 dimensiones |
| **Costo Aprox Indexación** | ~$0.10 USD | 280 chunks * 1k tokens * precio input |
| **Tiempo Retrieval** | ~200ms (Vector) + ~2s (Rerank) | Depende de latencia OpenAI API |

### Observaciones Finales del Auditor
El sistema presenta una arquitectura **muy robusta** para un entorno de producción. Destaca la decisión de usar **Normalización con LLM** (Fase 0) antes del chunking, lo cual es poco común pero extremadamente efectivo para documentos legales complejos. La orquestación con LangGraph proporciona una capacidad de "autocorrección" valiosa, aunque añade latencia. El uso de `gpt-4o` en todos los puntos de decisión (Normalizer, Reranker, Evaluator, Synthesis) garantiza calidad, pero implica un coste operativo por query alto que debería monitorizarse.
