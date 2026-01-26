# 🤖 Guía de Demostración: Sistema RAG Agéntico 11/10

**Objetivo**: Demostrar la superioridad del sistema agéntico frente a un chat documental tradicional.
**Audiencia**: Directivos, Oficiales de Adquisiciones, Auditores.

---

## 🏗️ Preparación del Entorno

1. **Limpieza Inicial**:
   ```bash
   python init_vectorstore.py
   ```
   *Asegúrese de responder 's' para tener una base limpia.*

2. **Lanzamiento del Dashboard**:
   ```bash
   streamlit run app.py
   ```
   *Abra [http://localhost:8501](http://localhost:8501) y maximice la ventana.*

---

## 🎭 El Guion de la Demo (The Pitch)

### Acto 1: La Transparencia del Razonamiento
*Objetivo: Mostrar que el sistema "piensa" antes de hablar.*

1. **Acción**: Escriba la consulta:
   > *"Compara el importe del contrato de IVECO con el de Vehículos Blindados"*
2. **Observación**:
   - Señale el spinner "🧠 Procesando inteligencia táctica...".
   - Explique que el **Agente Planificador** está clasificando la pregunta como "Simple" o "Agregación".
3. **Resultado**:
   - Muestre la respuesta concisa.
   - **Crucial**: Haga clic en la cita **[Doc: CON_2024_001...]** (si es clickeable) o mencione su existencia para validar la fuente.

### Acto 2: "El Tanque" (Prueba de Estrés / Agregación)
*Objetivo: Romper un RAG tradicional y ver cómo este sobrevive a consultas masivas.*

1. **Acción**: Lance el reto mayor:
   > *"¿Cuál es la suma total EXACTA de todos los avales bancarios y garantías técnicas listados en el sistema? Desglosa por contrato."*
2. **Narrativa mientras procesa**:
   - *"Fíjense que esta pregunta requiere leer TODOS los documentos."*
   - *"Un sistema normal colapsaría o alucinaría una cifra."*
   - *"Nuestros agentes están paralelizando la búsqueda (Retrieval) y filtrando ruido (Evaluator)."*
3. **Resultado**:
   - Espere la tabla detallada.
   - Verifique una cifra al azar abriendo el PDF correspondiente en la carpeta `data/contracts`.
   - Destaque la precisión del cálculo (ej. 2.9M€).

### Acto 3: La Autocrítica (Fail-Safe)
*Objetivo: Demostrar que el sistema prefiere admitir ignorancia a mentir.*

1. **Acción**: Pregunte algo que NO existe en los documentos:
   > *"¿Cuál es el presupuesto asignado para el Proyecto Espacial 'Estrella de la Muerte'?"*
2. **Resultado Esperado**:
   - El sistema debe responder: *"No consta información sobre dicho proyecto en la base de datos."*
   - Explique: *"El Agente Evaluador auditó los resultados, vio que no había coincidencia y bloqueó cualquier alucinación."*

### Acto 4: Análisis de Riesgos (Lógica Compleja)
*Objetivo: Mostrar razonamiento legal/financiero.*

1. **Acción**:
   > *"Identifica todos los contratos que tengan cláusulas de confidencialidad y lista sus fechas de vencimiento."*
2. **Observación**:
   - El sistema cruzará información de texto (cláusulas) con datos estructurados (fechas).

---

## 📊 Interpretación Visual para el Cliente

Muestre siempre estos elementos en la pantalla:

1. **Citas [Doc, Pág]**: "Esta es nuestra garantía forense. Cada palabra está respaldada."
2. **Logs (Terminal)**: Si hay personal técnico presente, muestre la terminal corriendo de fondo para ver:
   - `🤖 planner iniciando...`
   - `🔍 retrieval recuperando 15 chunks...`
   - `✅ synthesis completado`
   *Esto tangibiliza el trabajo de los agentes.*

---

## ⚠️ Preguntas Frecuentes (Objecciones)

- **"¿Por qué tarda 20-30 segundos?"**
  - *"Estamos haciendo el trabajo de un analista de 4 horas en 30 segundos. La precisión requiere verificación, no velocidad instantánea ciega."*

- **"¿Qué pasa si subo 10,000 contratos?"**
  - *"El sistema usa Token Budgeting para leer lo más relevante primero. Para volúmenes masivos, activamos el modo Map-Reduce (ya contemplado en la arquitectura)."*

---

**Cierre**: "Esto no es un buscador. Es su nuevo equipo de auditoría digital."
