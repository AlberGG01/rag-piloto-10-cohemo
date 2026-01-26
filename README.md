# 🛡️ Sistema de Control de Contratos de Defensa

Sistema de monitorización de contratos militares con IA local (GGUF) para garantizar seguridad y confidencialidad. **Funciona 100% offline** sin dependencias de APIs externas.

## 📋 Características

- **Informe Diario de Alertas**: Detecta automáticamente vencimientos de contratos, avales e hitos próximos
- **Chatbot RAG**: Consulta información de contratos mediante lenguaje natural
- **Envío de Email**: Reportes por SMTP con adjuntos Excel
- **100% Offline**: Todo funciona localmente sin conexión a internet

## ⚙️ Requisitos de Sistema

- **Python**: 3.10 o superior
- **RAM**: 8GB mínimo
- **Espacio**: 5GB (modelo + datos)
- **CPU**: Compatible con cualquier procesador x64
- **GPU**: No requerida (funciona solo con CPU)

## 🚀 Instalación

### 1. Clonar/Descargar el proyecto

```bash
cd "c:\Users\alber\Piloto Empresa\defense_contracts_system"
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

> ⚠️ **Nota sobre llama-cpp-python en Windows**: Si falla la instalación, puede necesitar Visual Studio Build Tools. Alternativa:
> ```bash
> pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
> ```

### 5. Descargar modelo GGUF

1. Ir a: https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF
2. Descargar el archivo: `Llama-3.2-3B-Instruct-Q4_K_M.gguf` (~2GB)
3. Colocar en: `models/llama-3.2-3b-instruct.Q4_K_M.gguf`

### 6. Configurar email (opcional)

Copiar `.env.example` a `.env` y configurar credenciales SMTP:

```bash
copy .env.example .env
```

Para Gmail, generar una "App Password":
1. Ir a https://myaccount.google.com/security
2. Activar verificación en 2 pasos
3. Ir a "Contraseñas de aplicaciones"
4. Generar contraseña para "Correo"
5. Usar esa contraseña de 16 caracteres en `.env`

### 7. Añadir contratos PDF

Colocar los archivos PDF de contratos en:
```
data/contracts/
```

### 8. Inicializar base vectorial

```bash
python init_vectorstore.py
```

### 9. Ejecutar aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en: http://localhost:8501

## 📁 Estructura del Proyecto

```
defense_contracts_system/
├── data/
│   ├── contracts/          # PDFs de contratos
│   ├── vectorstore/        # Base de datos ChromaDB
│   └── logs/               # Logs de la aplicación
├── models/
│   └── llama-3.2-3b-instruct.Q4_K_M.gguf
├── src/
│   ├── agents/             # Agentes de IA
│   ├── utils/              # Utilidades
│   └── graph/              # Workflow LangGraph
├── app.py                  # Dashboard Streamlit
├── init_vectorstore.py     # Script de inicialización
├── requirements.txt        # Dependencias
└── .env.example            # Ejemplo de configuración
```

## 📄 Formato de PDFs Esperado

Los PDFs deben tener secciones marcadas con delimitador `───`:

```
═══════════════════════════════════════════════════
CONTRATO DE [TIPO] - MINISTERIO DE DEFENSA
═══════════════════════════════════════════════════
EXPEDIENTE: CON_2024_001
─── PARTES CONTRATANTES ───
Contratante: ...
Contratista: ...
─── FECHAS RELEVANTES ───
Fecha de inicio: DD/MM/YYYY
Fecha de finalización: DD/MM/YYYY
─── GARANTÍAS Y AVALES ───
Aval bancario: XX.XXX,XX €
Fecha de vencimiento del aval: DD/MM/YYYY
...
```

## 🐛 Solución de Problemas

### Error: "Modelo no encontrado"
- Verificar que el archivo `.gguf` está en `models/`
- Verificar el nombre exacto del archivo

### Error: "No hay contratos"
- Añadir archivos PDF a `data/contracts/`
- Ejecutar `python init_vectorstore.py`

### El chatbot no responde
- Verificar que el modelo GGUF está cargado
- Verificar que se ejecutó `init_vectorstore.py`

### Email no se envía
- Verificar credenciales en `.env`
- Para Gmail, usar "App Password" no la contraseña normal
- Verificar que el antivirus no bloquea SMTP

### Error instalando llama-cpp-python
```bash
# Opción 1: Usar wheels precompilados
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Opción 2: Instalar Visual Studio Build Tools
# Descargar de: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Instalar "Desktop development with C++"
```

## 🔒 Seguridad

- ✅ Todo funciona offline sin conexión a internet
- ✅ No se envían datos a APIs externas
- ✅ Modelo de IA ejecutado localmente
- ✅ Datos almacenados solo en local
- ✅ Logs no contienen información confidencial

## 📞 Uso

1. **Generar Informe**: Pulsar "🚨 GENERAR INFORME DIARIO"
2. **Ver Alertas**: Tabla coloreada por prioridad
3. **Descargar Excel**: Botón "📥 Descargar Excel"
4. **Enviar Email**: Formulario con destinatario y texto
5. **Chatbot**: Escribir preguntas en el campo de chat

### Ejemplos de preguntas para el chatbot:
- "¿Cuántos contratos vencen en los próximos 30 días?"
- "¿Qué contratos tienen cláusula de revisión de precios?"
- "Resume las garantías del contrato CON_2024_001"
- "¿Cuál es el importe del contrato de uniformidad?"

---

**Sistema de Control de Contratos de Defensa v1.0**  
Funcionamiento 100% Offline | Modelo: Llama-3.2-3B-Instruct GGUF
