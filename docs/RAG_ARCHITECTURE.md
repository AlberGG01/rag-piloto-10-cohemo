# 🎓 Lección Magistral: Ingeniería de Sistemas RAG (Defense Contracts)

> **Profesor:** Principal Software Architect  
> **Tema:** Retrieval-Augmented Generation en Entornos Críticos  
> **Nivel:** Avanzado / Ingeniería de Precisión

---

Bienvenido al "quirófano". Hoy no vamos a ver diagramas de cajas bonitas. Vamos a abrir el código y entender la **física** detrás de nuestro sistema de IA. Olvida la magia; esto son matemáticas y algoritmos.

---

## 🏛️ 0. La Base Oculta: Normalización Semántica (The Structural Layer)

*Has preguntado: "¿Por qué el sistema busca delimitadores `───`? ¿De dónde salen?"*
Excelente pregunta. Aquí es donde ganamos o perdemos la batalla de la calidad.

### El Problema del PDF Crudo
Un PDF no es texto; es una sopa de letras posicionada en coordenadas X/Y.
*   Si lees un contrato con `pdfplumber` o `PyPDF2`, obtienes:
    *   Cabeceras de página repetidas en medio de frases: *"Cláusula 5... [COHEMO 2024 Pág 5] ...de rescisión."*
    *   Tablas rotas que se leen línea a línea en lugar de celda a celda.
    *   Notas al pie que rompen el flujo lógico.

Si pasas esta "basura" al Chunker, tendrás chunks rotos.

### La Solución: Fase 0 - Normalización con LLM (`src/utils/normalizer.py`)
Antes de que el RAG siquiera "vea" el documento, pasamos el texto crudo por un **LLM Normalizador (GPT-4o)**.

*   **Objetivo:** No es resumir. Es **Re-estructurar**.
*   **El Prompt Mágico:** Le ordenamos al modelo actuar como un "Experto en Estructuración".
    *   *"Detecta tablas y pásalas a Markdown."*
    *   *"Elimina números de página."*
    *   *Y lo más importante:* **"Inserta el delimitador `───` antes de cada sección lógica."**

> **Resultado:** El RAG no ingesta el PDF original. Ingesta una versión "Platónica" ideal del contrato, limpia y etiquetada. Por eso el Chunker (`chunking.py`) puede buscar `───` con confianza total. No adivina dónde acaba la cláusula; el Normalizador ya se lo ha dicho explícitamente.

---

## 🏛️ 1. Estrategia de Fragmentación (The Chunking Dilemma)

El primer error del novato es pensar que el texto es solo texto. Para una máquina, el texto es información espacial. Cómo cortamos ese texto define la "resolución" de nuestra base de datos.

### 🔬 Análisis del Splitter (`src/utils/chunking.py`)
No usamos un `CharacterTextSplitter` ingenuo. Usamos una **Estrategia Semántica Jerárquica**.

*   **Naive Splitting (Lo que NO hacemos):** Cortar cada 500 caracteres ciegamente.
    *   *Riesgo:* Cortarías una frase legal vital: *"El contratista pagará... [CORTE] ...una bonificación"*. El cambio de sentido es catastrófico.
*   **Nuestra Implementación (`subdivide_large_section`):**
    1.  **Detección de Fronteras:** Aprovechamos el trabajo de la Fase 0. Buscamos los `───` que insertó el Normalizador.
    2.  **Recursividad:** Si una sección mide >1000 tokens, no la cortamos arbitrariamente. Buscamos puntos y seguido.

### 📐 Justificación Matemática: La Teoría de la Dilución Vectorial

¿Por qué 1000 tokens y no 8000 (el límite del modelo)?

Imagina que un Embeddings es el **promedio semántico** de todas las palabras en el chunk.
$$ \vec{V}_{chunk} \approx \frac{1}{N} \sum_{i=1}^{N} \vec{v}_{palabra_i} $$

*   **Chunk Pequeño (100 tokens):** El vector es muy "puntiagudo". Apunta a un concepto muy específico (ej. "Penalización por mora"). **Alta Precisión, Bajo Contexto.**
*   **Chunk Gigante (8000 tokens):** Tienes el contrato entero. El vector es el promedio de "Penalización", "Objeto", "Precios", "Firmas".
    *   *Efecto:* El vector resultante se queda en el "centro" del espacio semántico. Se vuelve **gris**. No se parece a nada específico.
    *   *Consecuencia:* Cuando busques "Penalización", tu query (vector específico) estará lejos del vector del chunk gigante (vector promedio). **El sistema fallará en encontrarlo.**

> **Veredicto:** Elegimos 1000 tokens como el "punto dulce" donde hay suficiente contexto legal para entender la cláusula, pero suficiente especificidad para que el vector siga apuntando a un tema concreto.

---

## 🔎 2. Arquitectura de Recuperación (The Retriever Matrix)

No todos los Retrievers son iguales. Aquí justificamos nuestra elección.

### 📊 La Matriz de Comparación

| Tipo de Retriever | Descripción | ¿Por qué lo usamos/descartamos? |
| :--- | :--- | :--- |
| **Naive Retriever** | Query $\to$ Vector Search $\to$ Top K Chunks. | **Inuficiente.** Si un contrato repite la palabra "Vehículo" 200 veces, los Top-5 chunks vendrán *todos* del mismo documento. El usuario pierde la visión global. |
| **Parent Document Retriever** | Busca chunks pequeños, pero devuelve al LLM el "Documento Padre" entero. | **Descartado.** Los contratos de defensa son PDFs de 100 páginas. Inyectar el PDF entero satura la ventana de contexto de GPT-4o y dispara el coste. |
| **Hierarchical / Knowledge Graph** | Busca documentos primero, luego hace "Zoom-In" en sus partes. | **✅ ELEGIDO (`smart_retrieval.py`).** Nos permite diversidad (encontrar 5 contratos distintos) y precisión (encontrar la cláusula exacta dentro de ellos). |

### 🧠 Teoría Didáctica: El Desacople Index-Generation

En nuestra implementación (`smart_retrieval.py`), aplicamos un desacople crítico:
1.  **Indexación (Lo que buscamos):** Vectores densos de chunks enriquecidos.
2.  **Generación (Lo que le damos al LLM):** No solo el chunk. Inyectamos metadata (`num_contrato`, `importe`).

El vector en la base de datos es solo una "huella digital". Cuando la encontramos, no le damos al LLM la huella; le damos el objeto completo con sus etiquetas. Esto permite que el LLM diga: *"Según el Documento X..."* aunque esa etiqueta "Documento X" no fuera semanticamente relevante para la búsqueda vectorial per se.

### 🔬 Deep Dive: El Problema de la Diversidad (Naive vs Hierarchical)

*Preguntaste: "¿Por qué busca documentos primero? ¿Qué gano?"*

Imagina esta Query: **"¿Qué penalizaciones por retraso existen en mis contratos?"**

Supón que tienes 2 contratos:
*   **Contrato A (Gigante):** Menciona la palabra "penalización" 50 veces (en cada cláusula).
*   **Contrato B (Pequeño):** Menciona "penalización" solo 1 vez (en la cláusula clave).

#### Escenario 1: Naive Retrieval (Búsqueda Simple)
Pides los Top-10 chunks más similares.
*   **Resultado:** 10 chunks del **Contrato A**. (Porque al repetirlo tanto, estadísticamente inunda el Top).
*   **Efecto:** El LLM te responde: *"Solo veo penalizaciones en el Contrato A"*. **Has perdido el Contrato B.** El sistema es "ciego" a la diversidad.

#### Escenario 2: Hierarchical Retrieval (Nuestra Solución)
1.  **Fase de Exploración:** Pedimos los Top-50 chunks. (Aquí salen 45 de A y 5 de B).
2.  **Agrupación:**
    *   Doc A: Score promedio 0.95 (Muy relevante).
    *   Doc B: Score promedio 0.92 (Relevante).
3.  **Selección de Diversidad:** Elegimos los **Top Documentos Únicos**: [A, B].
4.  **Zoom-In (Snippet Selection):**
    *   De Doc A: Dame tus 3 mejores chunks.
    *   De Doc B: Dame tus 3 mejores chunks.
*   **Resultado Final al LLM:** 3 chunks de A + 3 chunks de B.
*   **Respuesta del Bot:** *"Se han encontrado penalizaciones en el Contrato A y TAMBIÉN en el Contrato B..."* -> **ÉXITO.**

---

## 🤖 3. La Orquestación Agéntica (El Cerebro Recursivo)

Aquí abandonamos los scripts lineales. Entramos en **Teoría de Control**.

### 🔄 Linealidad vs. Recursividad
*   **Flujo Lineal:** Input $\to$ Search $\to$ Generate.
    *   *Fallo:* El usuario pregunta algo ambiguo. La búsqueda falla. El sistema devuelve "No lo sé". Fin.
*   **Flujo Recursivo (Nuestro Sistema):**
    *   Input $\to$ Search $\to$ **Evaluate** $\to$ (¿Es suficiente?) $\to$ **NO** $\to$ **Corrective** $\to$ Search Again.
    *   *Analogía:* Es como un becario que no encuentra un archivo. En vez de rendirse (Lineal), vuelve a ti y te pregunta: *"¿Podría estar archivado con otro nombre?"* (Recursivo).

### 🚦 Toma de Decisiones (Routing Logic)
Analiza `src/agents/evaluator.py`.
La función de routing no es un `if keyword in text`. Es un **Juez LLM**.
*   Le damos al LLM los chunks recuperados y la pregunta.
*   Prompt: *"Teniendo estos datos, ¿puedes responder rigurosamente? Responde SUFFICIENT o INSUFFICIENT."*
*   Esta decisión es probabilística, no determinista. Es lo que hace al sistema "inteligente".

### 💾 Estado del Grafo (`src/graph/state.py`)
El `WorkflowState` es la memoria de corto plazo.
*   **Problema:** En recursividad, ¿cómo evitamos bucles infinitos?
*   **Solución:** Campo `retry_count`.
*   El grafo monitorea cuántas veces ha pasado por el nodo `corrective`. Si `retry_count > 3`, el sistema fuerza una salida (un "Circuit Breaker"), evitando gastar dinero infinito en un bucle sin solución.

---

## 🧠 4. El Post-Procesado (Re-ranking y Refinamiento)

### El "Segundo Filtro": Cross-Encoders
La base vectorial es "tonta". Usa **Similitud del Coseno**, que es geométrica.
*   *Query:* "Penalización por retraso"
*   *Chunk A:* "El retraso no conlleva penalización" (Negación).
*   *Chunk B:* "Se aplicará penalización por retraso" (Afirmación).

Para el vector, A y B son casi idénticos (comparten palabras clave). Tienen distancias muy cercanas.
Aquí entra el **Reranker (`src/utils/reranker.py`)**.
*   Actúa como un **Cross-Encoder**: Lee la Query y el Chunk A *juntos* y se pregunta: *"¿Responde esto realmente a la pregunta?"*
*   El LLM vería que el Chunk A niega la premisa y le bajaría el score, mientras que el Coseno lo puso arriba.
*   **Resultado:** Filtramos ruido semántico que matemáticamente parecía correcto pero lógicamente no lo era.

---

## 🧪 5. Guía de Supervivencia para el Junior

Si vas a tocar el código, lee esto antes de hacer `git commit`.

### 📍 Traceability (Dónde ocurre la magia)
*   **Si quieres cambiar el corte de texto:** `src/utils/chunking.py`, línea ~305 (`subdivide_large_section`) y `src/utils/normalizer.py` (el prompt).
*   **Si el bot alucina datos:** `src/agents/rag_agent.py`, busca `validate_response`. Aquí está el "Red Team" que frena las invenciones.
*   **Si la búsqueda falla:** `src/utils/smart_retrieval.py`, línea ~47. Revisa si `metadata_filters` está siendo demasiado agresivo y filtrando el documento correcto.

### 🔬 Laboratorio: Experimento Sugerido
¿Quieres entender el "Signal Dilution" en vivo?
1.  Ve a `src/config.py`.
2.  Cambia `CHUNK_MAX_TOKENS` de `1000` a `4000`.
3.  Borra la DB (`rm -rf data/vectorstore`) y regenera (`python init_vectorstore.py`).
4.  Pregunta por un dato muy específico (ej. "importe del aval del expediente 2024").
5.  **Observación:** Verás que el Retrieval falla o trae documentos irrelevantes. ¿Por qué? Porque el "vector promedio" del chunk de 4000 tokens se ha diluido tanto que ya no apunta a "avales", apunta a "contrato genérico".

---
## 📊 6. Métricas del Sistema Actual (Snapshot)

Estos son los "Constantes Físicas" de nuestro universo RAG a día de hoy:

*   **Volumen de Datos:**
    *   **Contratos Ingestados:** 20 documentos (PDFs originales en `data/contracts`).
    *   **Documentos Normalizados:** 20 documentos (Markdown estructurado en `data/normalized`).
*   **Configuración de Fragmentación (`src/config.py`):**
    *   **Max Tokens:** 1000 tokens (El "punto dulce" de granulidad).
    *   **Overlap:** 100 tokens (Para preservar contexto entre cortes).
*   **Motor Vetorial:**
    *   **Modelo de Embeddings:** `text-embedding-3-large` (3072 dimensiones).
    *   **Store:** ChromaDB (Persistencia local en `data/vectorstore`).

---
*Fin de la lección. Ahora, ve y compila.*
