# 🚨 REPORTE DE FALLO CRÍTICO: FASE 1 (RETRIEVAL)

**Estado:** ❌ FALLIDO
**Auditor:** QA Automation Agent
**Prueba:** Hybrid Search (ChromaDB + BM25)

---

## 📉 Resultados de la Auditoría

Se auditó el retrieval para 2 preguntas de control. **Ambas fallaron** en recuperar el contexto correcto en el Top 3.

### 1. Caso "Importe Retamares"
**Pregunta:** *¿Cuál es el importe exacto del contrato de Retamares?*
**Target:** `28.500.000,00` | `28.5M`

| Rank | Documento Recuperado | Score | Contenido (Snippet) | Resultado |
|------|----------------------|-------|---------------------|-----------|
| 1 | `SER_2024_008` (Transporte) | RRF: 0.0380 | *La Administración ostenta las siguientes prerrogativas...* | ❌ Boilerplate legal |
| 2 | `CON_2024_018` (Hangares) | RRF: 0.0272 | *Importe total: 15.8M...* | ❌ Contrato incorrecto |
| 3 | `CON_2024_005` (Munición) | RRF: 0.0265 | *Importe total: 890k...* | ❌ Contrato incorrecto |

**Análisis:**
El sistema recuperó "prerrogativas administrativas" (boilerplate común a todos los contratos) como Top 1. Luego trajo contratos aleatorios con la palabra "Importe total". **No priorizó "Retamares"**.

---

### 2. Caso "Aval IVECO"
**Pregunta:** *¿Cuál es el código de aval del contrato con IVECO?*
**Target:** `AV-2024-1717`

| Rank | Documento Recuperado | Score | Contenido (Snippet) | Resultado |
|------|----------------------|-------|---------------------|-----------|
| 1 | `SER_2024_013` (Formación) | RRF: 0.0910 | *La Administración ostenta las siguientes prerrogativas...* | ❌ Boilerplate legal |
| 2 | `CON_2024_016` (Visión) | RRF: 0.0289 | *Aval: AV-2024-1616...* | ❌ Aval incorrecto |
| 3 | `CON_2024_001` (Blindados) | RRF: 0.0288 | *Aval: AV-2024-5678...* | ❌ Aval incorrecto |

**Análisis:**
Nuevamente, texto legal boilerplate en Top 1. Luego recuperó documentos con "Aval" pero ignoró la keyword "IVECO".

---

## 🛑 DIAGNÓSTICO: BOILERPLATE POISONING

El retrieval está "intoxicado" por chunks repetitivos (texto legal, prerrogativas) que aparecen en los 20 documentos.
- **BM25** debería haber filtrado por "Retamares" o "IVECO", pero parece que el boilerplate tiene un score artificialmente alto (quizás por longitud o frecuencia de términos de la query como "contrato", "importe", "aval").
- **Vector Search** está colapsando en patrones semánticos genéricos ("cláusulas legales").

**Acción Requerida:** detener proceso y corregir estrategia de retrieval.
