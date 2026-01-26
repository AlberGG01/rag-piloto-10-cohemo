
def get_custom_css():
    """Retorna el CSS personalizado para la inyección."""
    return """
    <style>
        /* 1. FUENTES DE ALTA PRECISIÓN Y FUTURISMO */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700;800&display=swap');
        
        :root {
            /* PALETA: TACTICAL AUTHORITY */
            --void-black: #09090b;       /* Autoridad Absoluta */
            --cohemo-navy: #000080;      /* Identidad Corporativa */
            --cyber-cyan: #00f2ff;       /* Inteligencia Activa */
            --alert-red: #ff2a2a;        /* Crítico */
            --tech-gray: #f1f5f9;        /* Superficies */
            --pure-white: #ffffff;       /* Limpieza */
            
            --glass-panel: rgba(255, 255, 255, 0.95);
            --shadow-levitation: 0 10px 40px -10px rgba(0,0,128,0.15);
        }

        /* 2. UNIVERSO VISUAL: LIMPIEZA TÉCNICA */
        .stApp {
            font-family: 'Outfit', sans-serif;
            background-color: var(--pure-white) !important;
            color: var(--void-black) !important;
        }

        /* 3. SIDEBAR: COMANDO OBSIDIANA */
        [data-testid="stSidebar"] {
            background: linear-gradient(135deg, var(--cohemo-navy) 0%, #001f3f 100%) !important; /* GRADIENTE CORPORATIVO */
            border-right: 1px solid var(--void-black);
        }
        
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* 4. MÉTRICAS OBSIDIANA (SIDEBAR Y DASHBOARD) */
        /* Estilo base para tarjetas métricas (DASHBOARD) */
        div[data-testid="stMetric"]:not([data-testid="stSidebar"] [data-testid="stMetric"]) {
            background: linear-gradient(145deg, #ffffff, #f8fafc) !important;
            border: 1px solid #e2e8f0 !important;
            border-left: 6px solid var(--void-black) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: var(--shadow-levitation) !important;
            transition: transform 0.2s ease;
        }

        /* Dashobard Metrics Elements */
        div[data-testid="stMetric"]:not([data-testid="stSidebar"] [data-testid="stMetric"]) [data-testid="stMetricLabel"] {
            color: #64748b !important;
        }
        div[data-testid="stMetric"]:not([data-testid="stSidebar"] [data-testid="stMetric"]) [data-testid="stMetricValue"] {
            color: var(--void-black) !important;
        }

        /* 4b. SIDEBAR METRICS: FIX VISIBILIDAD CRÍTICO + GLOW REDUCIDO */
        [data-testid="stSidebar"] [data-testid="stMetric"] {
            background: #ffffff !important; /* Blanco Puro */
            border: none !important;
            border-left: 8px solid var(--cohemo-navy) !important; /* Acento Navy Solido */
            border-radius: 4px !important; /* Más cuadrado/táctico */
            padding: 15px !important;
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.3) !important; /* Sombra oscura fuerte para "flotar" */
        }

        /* FUERZA TEXTO NAVY EN SIDEBAR PARA QUE SE VEA SOBRE BLANCO */
        [data-testid="stSidebar"] [data-testid="stMetric"] label,
        [data-testid="stSidebar"] [data-testid="stMetric"] div,
        [data-testid="stSidebar"] [data-testid="stMetric"] span,
        [data-testid="stSidebar"] [data-testid="stMetric"] p {
            color: #000080 !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 2rem !important;
            color: #000080 !important;
            font-weight: 800 !important;
        }

        /* 3. RADIO BUTTONS: SELECCIÓN CLARÍSIMA */
        [data-testid="stRadio"] label {
            background: transparent !important;
            color: white !important;
            padding: 5px; cursor: pointer;
        }
        /* Opción Seleccionada: Cyan + Negrita */
        [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child[aria-checked="true"] + div {
            color: var(--cyber-cyan) !important;
            font-weight: 800 !important;
            text-shadow: 0 0 8px rgba(0, 242, 255, 0.5);
        }
        /* Circulo seleccionado */
        [data-testid="stRadio"] [data-baseweb="radio"] [aria-checked="true"] {
            background-color: var(--cyber-cyan) !important;
            border-color: var(--cyber-cyan) !important;
        }

        /* 5. HEADER: MARK AITHORITY */
        .main-header {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 3rem;
            text-transform: uppercase;
            letter-spacing: -0.05em;
            color: var(--void-black) !important;
            border-bottom: 4px solid var(--void-black);
            padding-bottom: 10px;
            margin-bottom: 40px;
            display: inline-block;
        }
        
        .main-header span {
            color: var(--cohemo-navy);
        }

        /* 6. CONSOLA DE CHAT TÁCTICA (EL FUTURO) */
        
        /* Contenedor Mensaje Usuario: COMANDO */
        .user-message-container {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 20px;
        }
        
        .user-bubble {
            background: linear-gradient(135deg, var(--cohemo-navy) 0%, #001f3f 100%) !important; /* BLUE CORPORATE (NAVY) */
            color: white !important;
            padding: 15px 25px;
            border-radius: 20px 20px 4px 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            box-shadow: 5px 5px 15px rgba(0, 0, 128, 0.2);
            border: 1px solid rgba(255,255,255,0.1);
            max-width: 80%;
        }

        /* Contenedor Mensaje IA: INFORME DE INTELIGENCIA */
        .bot-message-container {
            margin-bottom: 30px;
            animation: fadeIn 0.5s ease-out;
        }
        
        .bot-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-top: 4px solid var(--cyber-cyan); /* Señal de Inteligencia */
            border-radius: 12px;
            box-shadow: 0 10px 30px -5px rgba(0,0,0,0.05);
            overflow: hidden;
        }
        
        .bot-header {
            background: #f8fafc;
            padding: 8px 20px;
            border-bottom: 1px solid #e2e8f0;
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 0.75rem;
            letter-spacing: 0.1em;
            color: var(--cohemo-navy);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .bot-header::before {
            content: "●";
            color: var(--cyber-cyan);
            font-size: 1.2em;
            animation: blink 2s infinite;
        }
        
        .bot-content {
            padding: 25px;
            font-family: 'Outfit', sans-serif;
            color: var(--void-black);
            line-height: 1.6;
            font-size: 1rem;
        }
        
        /* ESTILOS DE MARKETING EN RESPUESTAS (MARKDOWN) */
        .bot-content strong {
            background: linear-gradient(120deg, rgba(0, 242, 255, 0.15) 0%, rgba(0, 242, 255, 0) 100%);
            color: var(--cohemo-navy);
            font-weight: 800;
            padding: 2px 4px;
            border-radius: 4px;
        }
        
        .bot-content code {
            background: #f1f5f9;
            color: #ef4444; /* Rojo táctico para códigos */
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
        }

        /* 7. INPUTS: TERMINAL TÁCTICA (LIGHT TECH) */
        .stTextInput input, .stTextArea textarea, [data-testid="stChatInput"] textarea {
            background: linear-gradient(90deg, #ffffff 90%, #eff6ff 100%) !important; /* Blanco preponderante a azul muy pálido */
            color: var(--void-black) !important; /* Texto oscuro para contraste */
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', monospace !important;
            transition: all 0.3s ease;
        }
        
        /* Placeholder styling */
        .stTextInput input::placeholder, 
        .stTextArea textarea::placeholder,
        [data-testid="stChatInput"] textarea::placeholder {
            color: #64748b !important;
            opacity: 0.8;
        }
        
        .stTextInput input:focus, 
        .stTextArea textarea:focus, 
        [data-testid="stChatInput"] textarea:focus {
            border-color: var(--cohemo-navy) !important;
            background: #ffffff !important;
            box-shadow: 0 0 10px rgba(0, 0, 128, 0.15) !important;
        }

        /* ESTILO ESPECÍFICO PARA EL BOTÓN DE ENVIAR (FLECHA) */
        [data-testid="stForm"] button {
            background: var(--cohemo-navy) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-size: 1.2rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }

        [data-testid="stForm"] button:hover {
            background: #1e3a8a !important; /* Un poco más claro al hover */
            transform: translateY(-1px);
            box-shadow: 0 0 10px rgba(37, 99, 235, 0.5) !important;
        }

        /* 8. BOTONES: INTERFAZ DE CONTROL */
        .stButton button {
            background: white !important;
            color: var(--void-black) !important;
            border: 2px solid var(--void-black) !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            box-shadow: 4px 4px 0px var(--void-black) !important; /* Sombra sólida táctica */
            transition: all 0.1s !important;
        }
        
        .stButton button:hover {
            transform: translate(-2px, -2px);
            box-shadow: 6px 6px 0px var(--void-black) !important;
        }
        
        .stButton button:active {
            transform: translate(2px, 2px);
            box-shadow: 0px 0px 0px var(--void-black) !important;
        }

        /* Botón Primario Sidebar: CELESTE CORPORATIVO (GRADIENTE) */
        [data-testid="stSidebar"] button {
            background: linear-gradient(135deg, #00f2ff 0%, #0ea5e9 100%) !important; /* Celeste (Cyan to Sky) */
            border: 1px solid #0ea5e9 !important;
            color: var(--cohemo-navy) !important; /* Texto Navy: Contraste Corporativo */
            font-weight: 800 !important;
            box-shadow: 0 4px 10px rgba(0, 242, 255, 0.3) !important;
        }



        /* Animaciones */
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* Ocultar instrucciones molestas */
        [data-testid="InputInstructions"] { display: none !important; }
    </style>
    """
