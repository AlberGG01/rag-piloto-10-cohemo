# 🛠️ Informe de Depuración Q3 y Optimización

**Fecha:** 27/01/2026
**Objetivo:** Investigar Regresión Q3 (Chunking/Metadata) y evitar crash del Reranker.

---

## 1. Inspección Forense de Metadata (Q3)

Se ha inspeccionado directamente ChromaDB para el contrato objetivo de la Q3: `SER_2024_015` (*Mantenimiento Flota C295*).

**Resultados del Script de Depuración (`scripts/debug_q3_metadata.py`):**
*   **Chunks Encontrados:** 11 chunks asociados a `SER_2024_015`.
*   **Campo `adjudicatario`:** ✅ **PRESENTE** y **CORRECTO**.
    *   Valor: `"Airbus Defence and Space S.A."`
    *   Esto descarta que la regresión se deba a que el "Metadata Patch" anterior fallase en este archivo.
*   **Conclusión:** La metadata está bien. La regresión en Q3 se debe probablemente a que el *Smart Query Analyzer* infiere filtros demasiado estrictos o la búsqueda híbrida inicial (BM25) no está ranking el chunk de la tabla financiera lo suficientemente alto entre los top 50, o el chunk quedó mal formado.

---

## 2. Implementación "Válvula de Seguridad"

Se ha modificado `src/utils/smart_retrieval.py` para evitar que un filtro mal inferido (cero resultados) devuelva una lista vacía y cause un fallo total (Recall 0).

**Nueva Lógica:**
```python
if metadata_filters:
    try:
        filtered_chunks = search(query, k=initial_k, where=metadata_filters)
    except:
        filtered_chunks = []

    # FALLBACK AUTOMÁTICO
    if not filtered_chunks:
        logger.warning("⚠️ FILTRO DEMASIADO ESTRICTO (0 resultados). Aplicando FALLBACK a búsqueda abierta.")
        metadata_filters = None 
        # El sistema procede automáticamente a Hybrid Search sin filtros
```

Esta medida asegura que si el analizador de queries se equivoca (ej. infiere `adjudicatario="Airbus"` pero en metadata está `"Airbus Defence"` y no hay coincidencia exacta), el sistema **no falla silenciosamente**, sino que intenta recuperar chunks por pura similitud semántica/BM25.

---

## 3. Optimización de Memoria (Anti-Crash)

Para evitar el colapso del modelo `BGE-M3` (Reranker) observado en la iteración 5 de la evaluación, se ha parcheado `scripts/evaluate_hard_mode.py`:

*   **Batching:** Procesamiento en bloques de 5 preguntas.
*   **Garbage Collection:** Llamada explícita a `gc.collect()` tras cada bloque.
*   **Cooldown:** `time.sleep(5)` para permitir liberar recursos del sistema.

---

## Estado Final
*   **Metadata:** Verificada Ok.
*   **Logic:** Fallback activo.
*   **Stability:** Script de evaluación robustecido.

Listo para re-lanzar evaluación completa o parcial.
