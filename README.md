# 🎖️ Sistema RAG de Contratos de Defensa
## Implementación de Referencia 11/10 para Análisis de Documentos Críticos

**Precisión:** 100% (30/30 Golden Dataset)  
**Filosofía:** Certeza Absoluta > Velocidad  
**Latencia Aceptable:** 10-30s para análisis riguroso

---

## 🎯 Características Únicas

### 1. **Motor de Búsqueda Híbrido**
- Vector Search (OpenAI `text-embedding-3-large`) + BM25
- Fusión con Reciprocal Rank Fusion (RRF)

### 2. **Inteligencia Anti-Boilerplate** 🔥
- Penaliza automáticamente cláusulas legales genéricas
- Prioriza chunks con metadata específica

### 3. **Integrity Guard (0% Pérdida de Datos)**
- Normalización GPT-4o con precisión quirúrgica
- Validación regex de CIFs, IBANs, fechas, importes

### 4. **U-Shape Context Positioning**
- Mitiga "Lost in the Middle"
- Coloca chunks críticos al inicio y final del contexto

### 5. **Router de Optimización de Costes**
- Queries simples → GPT-4o-mini
- Queries complejas → GPT-4o
- **Ahorro:** ~60% en costes API

---

## 📊 Rendimiento Validado

| Métrica | Valor | Contexto |
|---------|-------|----------|
| **Accuracy** | **100%** | 30 queries (numéricas, inferenciales, edge cases) |
| **Latencia Media** | ~14s | Aceptable para análisis crítico |
| **Recall @ 15** | ~98% | Chunks críticos en top-15 |
| **Ahorro Costes** | 60% | vs baseline GPT-4o puro |

---

## 🚀 Inicio Rápido
```bash
# 1. Clonar e instalar
git clone <tu-repo>
pip install -r requirements.txt

# 2. Configurar API keys
cp .env.example .env
# Editar .env con tu OpenAI API key

# 3. Indexar (usa los .md ya normalizados)
python scripts/init_vectorstore.py

# 4. Validar
python tests/run_golden_v4.py
# Esperado: ✅ 30/30 PASS

# 5. Lanzar interfaz
streamlit run app.py
```

---

## 🎯 Casos de Uso

**✅ Ideal para:**
- Contratos legales (cláusulas, comparativas, compliance)
- Defensa/Gobierno (RFPs, specs técnicas, clearances)
- Documentación médica (historiales, ensayos clínicos)
- Normativas (ISO, STANAG, regulaciones)

**❌ No apto para:**
- Chat casual (usa ChatGPT)
- Streaming en tiempo real (<5s requerido)
- Escritura creativa no estructurada

---

## 📖 Documentación

- [Arquitectura Completa](RAG_MASTER_BLUEPRINT.md) - Especificación técnica
- [Guía de Adaptación](CONTRIBUTING.md) - Cómo adaptar a tu dominio
- [Deployment](DEPLOYMENT.md) - Setup producción, Docker, K8s

---

## 🏗️ Componentes Clave

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Embeddings** | OpenAI `text-embedding-3-large` | Búsqueda semántica |
| **Vector DB** | ChromaDB | Almacenamiento vectorial |
| **Keyword Search** | RankBM25 | Matching léxico |
| **LLM** | GPT-4o / GPT-4o-mini | Generación |
| **Re-ranker** | BGE-M3 | Ranking final |
| **Frontend** | Streamlit | Interfaz usuario |

---

## 📦 Estructura
```
defense-rag-system/
├── src/              # Lógica core
├── scripts/          # Utilidades (normalización, indexación)
├── tests/            # Golden Dataset + validación
├── data/
│   ├── contracts/    # PDFs originales
│   ├── normalized/   # Markdown procesados
│   └── chroma_db/    # Base vectorial
└── app.py            # Streamlit
```

---

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guía de adaptación a nuevos dominios.

---

## 📜 Licencia

MIT - Ver [LICENSE](LICENSE)

---

**⭐ Si te ayuda, considera darle estrella al repo**

Hecho con ❤️ para análisis de documentos críticos
