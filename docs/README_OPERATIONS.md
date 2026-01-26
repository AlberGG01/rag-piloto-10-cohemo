# 🛡️ Sistema de Control de Contratos de Defensa - Manual de Operaciones

**Versión del Sistema**: 11/10 (Agentic RAG)
**Fecha de Actualización**: 23/01/2026
**Estado**: Producción (Stable)

---

## 1. Introducción

Bienvenido al **Sistema de Inteligencia Agéntica**, una plataforma diseñada para analizar contratos de defensa con precisión militar (>95%). A diferencia de un chat tradicional, este sistema utiliza **5 agentes especializados** (Planificador, Recuperador, Evaluador, Correctivo y Sintetizador) que trabajan en equipo para garantizar que ninguna pregunta quede sin una respuesta fundamentada.

Este documento es la guía maestra para operar, configurar y mantener el sistema.

---

## 2. Anatomía del Proyecto

Entender la estructura es clave para la operación eficiente:

| Ruta | Descripción |
|------|-------------|
| `src/agents/` | **El Cerebro**. Contiene los 5 agentes (`planner`, `retrieval`, `evaluator`, `corrective`, `synthesis`). |
| `src/graph/` | **El Sistema Nervioso**. `workflow.py` define cómo fluyen los datos entre agentes usando LangGraph. |
| `src/utils/` | **Herramientas**. `vectorstore.py` (ChromaDB), `token_counter.py` (Control de costes), `llm_config.py` (Conexión OpenAI). |
| `data/contracts/` | **La Fuente**. Aquí se depositan los PDFs originales. |
| `data/normalized/` | **Procesado**. Archivos Markdown limpios generados por el normalizador. |
| `init_vectorstore.py` | **Script Crítico**. Carga los datos en la base vectorial. |
| `app.py` | **Interfaz**. Dashboard web construido con Streamlit. |

---

## 3. Preparación de Datos (Ingestión)

Para que el sistema sepa sobre nuevos contratos, siga este protocolo:

### Paso 1: Carga de Documentos
Deposite los nuevos archivos PDF en la carpeta:
`c:\Users\alber\Piloto Empresa\defense_contracts_system\data\contracts\`

### Paso 2: Normalización (Opcional pero Recomendado)
Si los PDFs son escaneados o complejos, ejecute el normalizador para convertirlos a texto limpio:
```bash
python normalize_all.py
```

### Paso 3: Indexación Vectorial
Este es el paso más importante. Convierte los textos en vectores buscables.
**Comando**:
```bash
python init_vectorstore.py
```
*Siga las instrucciones en pantalla. Si se le pregunta si desea reiniciar la base de datos, responda 's' para una recarga limpia.*

---

## 4. Ejecución del Sistema

Existen dos formas de interactuar con la inteligencia agéntica:

### Opción A: Dashboard Visual (Recomendado)
Interfaz web con chat, gráficas y gestión de alertas.

1. **Lanzar**:
   ```bash
   streamlit run app.py
   ```
2. **Acceso**: Abra su navegador en `http://localhost:8501`.
3. **Uso**: Vaya a la pestaña "💬 ASISTENTE IA" y escriba su consulta.

### Opción B: Ejecución por Terminal (Para Pruebas)
Ideal para verificar una query específica o depurar.

1. **Lanzar script de prueba**:
   ```bash
   python test_end_to_end.py
   ```
   *Esto ejecutará una consulta de prueba predefinida y mostrará el proceso paso a paso.*

---

## 5. Configuración y Tuning

El sistema está pre-calibrado, pero puede ajustarse en `src/config.py` y `src/utils/token_counter.py`.

### Control de Token Budgeting (Costes y Límites)
Para evitar errores de "Rate Limit" o facturas altas.
- **Archivo**: `src/utils/token_counter.py`
- **Variable**: `MAX_CONTEXT_TOKENS = 20000`
- *Acción*: Reduzca a 10000 si enfrenta errores 429 frecuentes. Aumente si necesita más detalle y tiene un Tier alto.

### Ajuste de Reintentos (Robustez)
Si la API de OpenAI es inestable.
- **Archivo**: `src/agents/base_agent.py`
- **Decorador**: `@retry(stop=stop_after_attempt(3), ...)`
- *Acción*: Cambie `stop_after_attempt(3)` a 5 para mayor persistencia (aumentará la latencia).

---

## 6. Interpretación de Resultados

### Citas de Fuentes
Cada afirmación clave incluirá una etiqueta de trazabilidad:
> "El importe es 2M€ **[Doc: CON_2024_001.pdf, Pág: 12]**"
- **Doc**: Nombre del archivo original.
- **Pág**: Página física donde se encontró el dato.

### Estados de Evaluación (Logs)
El `EvaluationAgent` juzga la calidad de la búsqueda antes de responder:
- **SUFFICIENT**: "Tengo todo lo necesario". (Pasa a síntesis).
- **PARTIAL/INSUFFICIENT**: "Falta información". (Activa al `CorrectiveAgent` para buscar de nuevo).

---

## 7. Mantenimiento y Solución de Problemas

### Error 429: "Rate Limit Exceeded"
**Síntoma**: El sistema se detiene o lanza un error de "Too Many Requests".
**Solución**:
1. El sistema tiene "Exponential Backoff" automático. Espere unos minutos.
2. Si persiste, reduzca `MAX_CONTEXT_TOKENS` en `token_counter.py`.

### Respuesta "No consta"
**Síntoma**: El sistema dice que no hay información sobre un contrato que usted sabe que existe.
**Solución**:
1. Verifique que el PDF esté en `data/contracts/`.
2. Ejecute `python init_vectorstore.py` para asegurar que está indexado.

### Migración a Escala Masiva (Futuro)
Si cargan >500 contratos y las consultas de "resumen total" fallan:
- Considere migrar el `SynthesisAgent` a una arquitectura **Map-Reduce** (procesar documentos en lotes pequeños y luego resumir los resúmenes), como se detalla en el plan de escalabilidad.

---

**Soporte Técnico**: Equipo de IA de COHEMO.
