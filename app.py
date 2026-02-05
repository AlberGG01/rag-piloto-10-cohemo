# -*- coding: utf-8 -*-
"""
Sistema de Control de Contratos de Defensa
Dashboard principal de Streamlit (Rediseñado v2.0)
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
import sys

# Configurar path para imports
from src.config import (
    CONTRACTS_PATH, 
    LOGS_PATH, 
    LOGS_FILE
)
from src.utils.pdf_processor import get_contracts_count
from src.utils.vectorstore import (
    is_vectorstore_initialized, 
    clear_collection,
    add_documents
)
from src.utils.chunking import create_all_chunks
from src.utils.llm_config import is_model_available, get_model_info
from src.utils.email_sender import send_daily_report, send_email, is_email_configured
from src.graph.reporting import run_quick_analysis
from src.agents.rag_agent import chat
from src.ui.styles import get_custom_css

# ============================================
# CONFIGURACIÓN DE LOGGING
# ============================================
LOGS_PATH.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOGS_FILE),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================
st.set_page_config(
    page_title="COHEMO - AI Procurement System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectar CSS personalizado
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ============================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================
if 'informe' not in st.session_state:
    st.session_state['informe'] = None
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if 'vectorstore_loaded' not in st.session_state:
    st.session_state['vectorstore_loaded'] = is_vectorstore_initialized()
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = None
if 'excel_path' not in st.session_state:
    st.session_state['excel_path'] = None
if 'alerts_summary' not in st.session_state:
    st.session_state['alerts_summary'] = {"total": 0, "high": 0, "medium": 0, "low": 0}
if 'pending_query' not in st.session_state:
    st.session_state['pending_query'] = None
if 'alerts_loaded' not in st.session_state:
    # Cargar alertas automáticamente al iniciar
    st.session_state['alerts_loaded'] = True
    try:
        with st.spinner("🚀 Iniciando protocolos de defensa y analizando contratos... (Esto puede tardar unos segundos)"):
            result = run_quick_analysis()
            if result.get("success"):
                st.session_state['alerts_summary'] = result.get("alerts_summary", {})
                # NO guardamos el informe aquí para que el dashboard muestre el mensaje de bienvenida
    except Exception:
        pass  # Si falla, simplemente no hay alertas


# ============================================
# FUNCIONES DE UI
# ============================================

def sidebar_section():
    """Genera la barra lateral con controles y métricas."""
    with st.sidebar:
        # Logo COHEMO
        logo_path = Path("assets/cohemo_logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown("# 🛡️ COHEMO AI")
        st.markdown("---")
        
        # 1. Métricas Clave
        st.subheader("📊 Estado del Sistema")
        
        contracts_count = get_contracts_count()
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Contratos", contracts_count)
        with col_m2:
            high_alerts = st.session_state.get('alerts_summary', {}).get('high', 0)
            st.metric("Alertas 🔴", high_alerts)
        
        st.markdown("---")
        
        # 2. Acciones Principales
        st.subheader("⚡ Acciones")
        
        if st.button("🚨 ANÁLISIS DIARIO", type="primary", use_container_width=True):
            generate_report()
            
        if st.button("🔄 RECARGAR VECTOR DB", use_container_width=True):
            reload_contracts()
            
        st.markdown("---")
        
        # 3. Motor IA (Solo Informativo)
        st.subheader("🤖 Motor IA")
        st.success("🧠 Agentic Brain (OpenAI GPT-4o)", icon="✨")
        
        st.markdown("---")
            
        # 4. Configuración / Info
        with st.expander("⚙️ Configuración"):
            st.caption(f"Vectorstore: {'✅' if is_vectorstore_initialized() else '❌'}")
            st.caption(f"Logs: {LOGS_FILE}")
            
        st.caption(f"v11.10 | Agentic RAG")


def dashboard_tab():
    """Pestaña del Dashboard de Análisis."""
    st.markdown('<div class="main-header">PANEL DE CONTROL DE CONTRATOS</div>', unsafe_allow_html=True)
    
    if st.session_state.get('informe') is not None:
        # Resumen con tarjetas de colores
        summ = st.session_state['alerts_summary']
        
        # HTML personalizado para métricas con Diseño Cyber-Enterprise Premium
        st.markdown(f"""
        <div style="display: flex; gap: 20px; margin-bottom: 40px;">
            <div style="flex: 1; background: linear-gradient(145deg, #ffffff 0%, #f1f5f9 100%); padding: 28px; border-radius: 20px; border: 1px solid #e2e8f0; border-left: 6px solid #000080; box-shadow: 8px 8px 16px #d1d9e6, -8px -8px 16px #ffffff; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; padding: 10px; opacity: 0.1; font-size: 3rem;">📊</div>
                <div style="color: #64748b; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; font-family: 'Outfit', sans-serif;">Total Contratos Analizados</div>
                <div style="color: #000080; font-size: 3rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1;">{summ.get('contracts_count', 0)}</div>
                <div style="margin-top: 8px; font-size: 0.75rem; color: #000080; font-weight: 700; opacity: 0.7;">TOTAL ALERTA: {summ.get('alerts_total', 0)}</div>
            </div>
            <div style="flex: 1; background: linear-gradient(145deg, #fffcfc 0%, #fff1f1 100%); padding: 28px; border-radius: 20px; border: 1px solid #fee2e2; border-left: 6px solid #ef4444; box-shadow: 8px 8px 16px #d1d9e6, -8px -8px 16px #ffffff; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; padding: 10px; opacity: 0.1; font-size: 3rem;">🚨</div>
                <div style="color: #b91c1c; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; font-family: 'Outfit', sans-serif;">Alertas de Prioridad ALTA</div>
                <div style="color: #ef4444; font-size: 3rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1;">{summ.get('high', 0)}</div>
                <div style="margin-top: 8px; border-radius: 4px; background: #fee2e2; display: inline-block; padding: 2px 8px; font-size: 0.7rem; color: #ef4444; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">Acción Inmediata</div>
            </div>
            <div style="flex: 1; background: linear-gradient(145deg, #fffdfa 0%, #fff8eb 100%); padding: 28px; border-radius: 20px; border: 1px solid #fef3c7; border-left: 6px solid #f59e0b; box-shadow: 8px 8px 16px #d1d9e6, -8px -8px 16px #ffffff; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; padding: 10px; opacity: 0.1; font-size: 3rem;">⚠️</div>
                <div style="color: #b45309; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; font-family: 'Outfit', sans-serif;">Alertas de Prioridad MEDIA</div>
                <div style="color: #f59e0b; font-size: 3rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1;">{summ.get('medium', 0)}</div>
                <div style="margin-top: 8px; border-radius: 4px; background: #fef3c7; display: inline-block; padding: 2px 8px; font-size: 0.7rem; color: #f59e0b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">Bajo Revisión</div>
            </div>
            <div style="flex: 1; background: linear-gradient(145deg, #fafffa 0%, #f0fdf4 100%); padding: 28px; border-radius: 20px; border: 1px solid #dcfce7; border-left: 6px solid #10b981; box-shadow: 8px 8px 16px #d1d9e6, -8px -8px 16px #ffffff; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; padding: 10px; opacity: 0.1; font-size: 3rem;">✅</div>
                <div style="color: #15803d; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; font-family: 'Outfit', sans-serif;">Contratos SIN RIESGO</div>
                <div style="color: #10b981; font-size: 3rem; font-weight: 800; font-family: 'JetBrains Mono', monospace; line-height: 1;">{summ.get('contracts_clean', 0)}</div>
                <div style="margin-top: 8px; border-radius: 4px; background: #dcfce7; display: inline-block; padding: 2px 8px; font-size: 0.7rem; color: #10b981; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">Estado Nominal</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Detalle de Alertas")
        
        df = st.session_state['informe']
        
        # Estilizar tabla
        def color_map(val):
            if isinstance(val, str):
                if '🔴' in val: return 'background-color: #5e2a2a; color: #ffcccc'
                if '🟡' in val: return 'background-color: #5e5e2a; color: #ffffcc'
                if '🟢' in val: return 'background-color: #2a5e2a; color: #ccffcc'
            return ''

        st.dataframe(
            df.style.applymap(color_map, subset=['Prioridad']),
            use_container_width=True,
            height=400
        )
        
        # Descarga
        if st.session_state.get('excel_path'):
            with open(st.session_state['excel_path'], 'rb') as f:
                st.download_button(
                    "📥 Descargar Reporte Excel",
                    f,
                    file_name=f"reporte_defensa_{datetime.now().strftime('%Y%m%d')}.xlsx"
                )
    else:
        st.markdown(f"""
        <div style="background: #ffffff; padding: 50px; border-radius: 20px; border: 1px solid #e2e8f0; border-top: 6px solid #00f2ff; box-shadow: 0 20px 50px -10px rgba(0,0,128,0.1); text-align: center; position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; color: #f8fafc; font-size: 15rem; font-weight: 800; z-index: 0;">AI</div>
            <div style="position: relative; z-index: 1;">
                <h2 style="color: #09090b !important; margin-bottom: 10px; font-weight: 800; font-size: 2.5rem; letter-spacing: -1px; text-transform: uppercase;">
                    <span style="color: #000080;">COHEMO</span> INTELLIGENCE SYSTEM
                </h2>
                <div style="background: #09090b; color: #00f2ff; display: inline-block; padding: 5px 15px; border-radius: 50px; font-family: 'JetBrains Mono'; font-size: 0.8rem; font-weight: 700; margin-bottom: 30px; letter-spacing: 1px;">
                    ● SYSTEM ONLINE
                </div>
                <p style="color: #4b5563 !important; font-size: 1.2rem; max-width: 700px; margin: 0 auto 40px; line-height: 1.6;">
                    Plataforma de auditoría táctica y análisis de riesgos. El futuro de la gestión de defensa está activo.
                </p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: left;">
                    <div style="padding: 25px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 20px rgba(0,0,0,0.03); transition: transform 0.2s;">
                        <h4 style="color: #09090b !important; margin-bottom: 10px; font-weight: 800;">🔍 Auditoría Deep-Scan</h4>
                        <p style="font-size: 0.9rem; color: #64748b !important;">Extracción de precisión militar de cláusulas y datos financieros en documentos PDF.</p>
                    </div>
                    <div style="padding: 25px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 20px rgba(0,0,0,0.03); transition: transform 0.2s;">
                        <h4 style="color: #09090b !important; margin-bottom: 10px; font-weight: 800;">🛡️ Control de Activos</h4>
                        <p style="font-size: 0.9rem; color: #64748b !important;">Vigilancia activa de avales y garantías. Nada escapa al control del sistema.</p>
                    </div>
                    <div style="padding: 25px; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 20px rgba(0,0,0,0.03); transition: transform 0.2s;">
                        <h4 style="color: #09090b !important; margin-bottom: 10px; font-weight: 800;">🧠 Neural Assistant</h4>
                        <p style="font-size: 0.9rem; color: #64748b !important;">Consultas estratégicas en lenguaje natural con razonamiento avanzado.</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def chatbot_tab():
    """Pestaña del Asistente IA."""
    st.markdown('<div class="main-header">COHEMO - ASISTENTE DE INTELIGENCIA MILITAR</div>', unsafe_allow_html=True)
    
    # Contenedor de chat con scroll
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state['messages']:
            st.markdown("""
            <div style="text-align: center; padding: 40px; color: #666;">
                <h3>🤖 Listo para recibir órdenes</h3>
                <p>Pregunta sobre importes, fechas, avales o detalles técnicos.</p>
            </div>
            """, unsafe_allow_html=True)
            
        for msg in st.session_state['messages']:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="user-message-container">
                    <div class="user-bubble">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:

                # Mostrar respuesta con formato markdown
                st.markdown(f"""
                <div class="bot-message-container">
                    <div class="bot-card">
                        <div class="bot-header">🛡️ INTELLIGENCE REPORT</div>
                        <div class="bot-content">{msg["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # ⭐ CITATION ENGINE SOURCES ⭐
                if msg.get("sources"):
                    with st.expander("📄 Fuentes Consultadas"):
                        for source in msg["sources"]:
                             # Fallback safe
                            archivo = source.get('archivo', 'Unknown')
                            contrato = source.get('num_contrato', 'N/A')
                            nivel = source.get('nivel_seguridad', 'N/A')
                            st.markdown(f"**📎 {archivo}**")
                            st.caption(f"Expediente: {contrato} | Clasificación: {nivel}")
                
                # ⭐ CONTRADICTIONS ⭐
                if msg.get("contradictions"):
                    st.divider()
                    st.warning("⚠️ **CONTRADICCIONES DETECTADAS**")
                    for cont in msg["contradictions"]:
                        st.error(cont.get("text", "Discrepancia detectada."))
                        if cont.get("requires_human_review"):
                            st.info("🔍 Requiere revisión manual por experto")
                
                # ⭐ CONFIDENCE SCORING ⭐
                if msg.get("confidence"):
                    conf = msg["confidence"]
                    sco = conf.get("confidence", 0)
                    rec = conf.get("recommendation", "")
                    
                    st.metric(
                        label="📊 Confianza de la Respuesta",
                        value=f"{sco}%",
                        delta=rec,
                        delta_color="normal" if sco >= 70 else "inverse"
                    )
                    
                    with st.expander("📊 Desglose de Confianza"):
                        st.subheader("Factores de Calidad")
                        for factor, score in conf.get("breakdown", {}).items():
                            color = "green" if score >= 70 else "orange" if score >= 40 else "red"
                            st.markdown(f"**{factor.replace('_', ' ').title()}:** {score}/100")
                            st.progress(score / 100)
                        
                        st.divider()
                        
                        fcts = conf.get("factors", {})
                        c1, c2 = st.columns(2)
                        with c1:
                            st.caption(f"Chunks analizados: {fcts.get('chunks_analyzed')}")
                        with c2:
                            st.caption(f"Score top chunk: {fcts.get('top_chunk_score', 0.0):.2f}")
                
                # Mostrar validación si existe
                if msg.get("validation"):
                    val = msg["validation"]
                    if val.get("overall_valid") is not None: # Check simple de estructura
                        with st.expander("🛡️ Validación de Respuesta"):
                            c1, c2, c3 = st.columns(3)
                            
                            # Integridad Numérica
                            num_ok = val["numerical"]["valid"]
                            c1.metric(
                                "Integridad Numérica",
                                "✅ OK" if num_ok else "❌ FAIL",
                                f"{val['numerical']['numbers_checked']} nums"
                            )
                            
                            # Coherencia Lógica
                            log_ok = val["logical"]["valid"]
                            c2.metric(
                                "Coherencia Lógica",
                                "✅ OK" if log_ok else "❌ FAIL",
                                f"{int(val['logical']['confidence']*100)}% conf"
                            )
                            
                            # Citación
                            cit_ok = val["citation"]["valid"]
                            c3.metric(
                                "Citación",
                                "✅ OK" if cit_ok else "⚠️ PARCIAL",
                                f"{int(val['citation']['citation_rate']*100)}% curado"
                            )
                            
                            # Recomendación
                            if val.get("recommendation"):
                                st.info(val["recommendation"])
                            
                            # Violaciones
                            if not num_ok and val["numerical"].get("violations"):
                                st.error("**Violaciones Numéricas:**")
                                for v in val["numerical"]["violations"]:
                                    st.write(f"- {v['number']} ({v['type']}): {v['reason']}")
        
        # Si hay una query pendiente, mostrar indicador de typing
        if st.session_state.get('pending_query'):
            st.markdown('<div class="typing-indicator"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
    
    # Procesar query pendiente (segunda fase)
    if st.session_state.get('pending_query'):
        query = st.session_state['pending_query']
        st.session_state['pending_query'] = None
        
        try:
            history = st.session_state['messages'][:-1]
            
            # SPINNER: Aquí es donde debe ocurrir la espera visible
            with st.spinner("🧠 Procesando inteligencia táctica..."):
                result = chat(query, history=history)
                
            # Extraer campos estructurados del resultado (que es un dict)
            msg = {
                "role": "assistant",
                "content": result.get("response", "Sin respuesta"),
                "validation": result.get("validation"),
                "confidence": result.get("confidence"),
                "sources": result.get("sources", []),
                "contradictions": result.get("contradictions", [])
            }
            st.session_state['messages'].append(msg)
        except Exception as e:
            st.session_state['messages'].append({"role": "assistant", "content": f"⚠️ Error: {str(e)}"})
        
        st.rerun()
    
    # Input fijo abajo
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
    
    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([6, 1])
        with cols[0]:
            user_input = st.text_input("Consulta:", placeholder="Escribe tu pregunta...", label_visibility="collapsed")
        with cols[1]:
            submit = st.form_submit_button("➤")
            
    if submit and user_input:
        # FASE 1: Añadir mensaje del usuario y guardar query pendiente
        st.session_state['messages'].append({"role": "user", "content": user_input})
        st.session_state['pending_query'] = user_input
        st.rerun()  # Rerun para mostrar mensaje inmediatamente
        
    # Botones inferiores (Limpiar / Exportar)
    if st.session_state['messages']:
        st.markdown("---")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("🗑️ LIMPIAR CHAT", use_container_width=True):
                st.session_state['messages'] = []
                st.session_state['pending_query'] = None
                st.rerun()
        with col_b2:
            # Opción de copiar todo para Email
            conv_text = ""
            for msg in st.session_state['messages']:
                role = "🟢 PREGUNTA" if msg['role'] == 'user' else "🛡️ RESPUESTA"
                conv_text += f"**{role}**:\n{msg['content']}\n\n---\n\n"
            
            with st.expander("📄 COPIAR CONVERSACIÓN", expanded=False):
                st.write("Copia este bloque para pegarlo en tu gestor de correo:")
                st.code(conv_text, language="markdown")
                st.download_button(
                    label="💾 DESCARGAR LOG",
                    data=conv_text,
                    file_name="cohemo_intelligence_log.md",
                    mime="text/markdown",
                    use_container_width=True
                )



# ============================================
# LÓGICA DE NEGOCIO
# ============================================

def process_chat_query(query):
    """Procesa la consulta del chat."""
    # NO añadir el mensaje aquí, ya se añadió en el evento del formulario.
    # Si 'pending_query' viene del formulario, ya está en st.session_state['messages'].
    
    try:
        # Contexto: todos los mensajes MENOS el último (que es el query actual)
        # Esto asegura que el historial NO incluya la pregunta que estamos respondiendo ahora mismo
        history = st.session_state['messages'][:-1]
        
        # Simular "pensando"
        with st.spinner("🧠 Procesando inteligencia..."):
            result = chat(query, history=history) # Ahora retorna dict
        
        # Extraer respuesta y validación
        response_text = result["response"]
        validation_data = result.get("validation")
        confidence_data = result.get("confidence")
        sources = result.get("sources", [])
        contradictions = result.get("contradictions", [])
        
        msg = {
            "role": "assistant", 
            "content": response_text,
            "validation": validation_data,
            "confidence": confidence_data,
            "sources": sources,
            "contradictions": contradictions
        }
        
        st.session_state['messages'].append(msg)
        logger.info(f"Chat query procesada: {query[:30]}...")
        
    except Exception as e:
        error_msg = f"⚠️ Error en sistema táctico: {str(e)}"
        st.session_state['messages'].append({"role": "assistant", "content": error_msg})


def reload_contracts():
    with st.spinner("🔄 Reindexando base de datos táctica..."):
        try:
            clear_collection()
            chunks = create_all_chunks()
            if chunks:
                add_documents(chunks)
                st.session_state['vectorstore_loaded'] = True
                st.success(f"✅ Base de datos actualizada: {len(chunks)} fragmentos.")
            else:
                st.warning("⚠️ Sin datos.")
        except Exception as e:
            st.error(f"❌ Error crítico: {str(e)}")


def generate_report():
    with st.spinner("🔄 Ejecutando análisis de inteligencia..."):
        result = run_quick_analysis()
        if result.get("success"):
            st.session_state['informe'] = result.get("dataframe")
            st.session_state['excel_path'] = result.get("excel_path")
            st.session_state['alerts_summary'] = result.get("alerts_summary", {})
            
            # AUTO-ENVIAR EMAIL con resumen
            if is_email_configured():
                summ = st.session_state['alerts_summary']
                resumen = f"""RESUMEN DE SITUACIÓN CONTRATOS:
• Contratos Analizados: {summ.get('contracts_count', 0)}
• Total Alertas: {summ.get('alerts_total', 0)}
• Prioridad ALTA: {summ.get('high', 0)} (crítico)
• Prioridad MEDIA: {summ.get('medium', 0)} (atención)
• Prioridad BAJA: {summ.get('low', 0)} (normal)

Se adjunta el informe completo en Excel."""
                
                success, msg = send_daily_report(
                    recipient="",  # Usa DEFAULT_RECIPIENT del .env
                    body=resumen,
                    excel_path=result.get("excel_path")
                )
                if success:
                    st.success("✅ Informe generado y enviado por email.")
                else:
                    st.warning(f"✅ Informe generado. ⚠️ Email: {msg}")
            else:
                st.success("✅ Informe generado. (Email no configurado)")
        else:
            st.error(f"❌ Fallo en análisis: {result.get('error')}")


# ============================================
# LAYOUT PRINCIPAL
# ============================================

def email_tab():
    """Pestaña de envío manual de emails."""
    st.markdown('<div class="main-header">ENVIAR INFORME POR EMAIL</div>', unsafe_allow_html=True)
    
    if not is_email_configured():
        st.error("❌ Email no configurado. Añade SMTP_USER y SMTP_PASSWORD en .env")
        return
    
    # Formulario de envío
    with st.form("email_form"):
        st.subheader("📧 Componer Email")
        
        destinatario = st.text_input(
            "Destinatario:",
            placeholder="ejemplo@empresa.com",
            help="Deja vacío para usar el destinatario por defecto"
        )
        
        asunto = st.text_input(
            "Asunto:",
            value=f"Informe de Contratos - {datetime.now().strftime('%d/%m/%Y')}"
        )
        
        contenido = st.text_area(
            "Contenido del mensaje:",
            height=200,
            placeholder="Escribe el contenido del email aquí..."
        )
        
        # Opción de adjuntar informe
        adjuntar = st.checkbox(
            "📎 Adjuntar último informe Excel",
            value=True,
            disabled=not st.session_state.get('excel_path')
        )
        
        if not st.session_state.get('excel_path'):
            st.caption("⚠️ No hay informe generado. Ejecuta 'Análisis Diario' primero.")
        
        enviado = st.form_submit_button("📤 Enviar Email", type="primary")
        
        if enviado:
            if not contenido.strip():
                st.error("El contenido del email no puede estar vacío")
            else:
                with st.spinner("📨 Enviando email..."):
                    excel = st.session_state.get('excel_path') if adjuntar else None
                    success, msg = send_email(
                        recipient=destinatario,
                        subject=asunto,
                        body=contenido,
                        attachment_path=excel
                    )
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
    
    # Mostrar resumen de alertas si hay informe
    if st.session_state.get('alerts_summary'):
        st.markdown("---")
        st.subheader("📋 Resumen para copiar")
        summ = st.session_state['alerts_summary']
        resumen_texto = f"""RESUMEN DE SITUACIÓN CONTRATOS ({datetime.now().strftime('%d/%m/%Y')}):
• Contratos Analizados: {summ.get('contracts_count', 0)}
• Contratos sin Incidencias: {summ.get('contracts_clean', 0)}
• Total Alertas Detectadas: {summ.get('alerts_total', 0)}
• Alertas PRIORIDAD ALTA: {summ.get('high', 0)}
• Alertas PRIORIDAD MEDIA: {summ.get('medium', 0)}"""
        st.code(resumen_texto, language=None)


sidebar_section()

# Tabs principales
tab_dash, tab_chat, tab_email = st.tabs(["📊 DASHBOARD TÁCTICO", "💬 ASISTENTE IA", "📧 EMAIL"])

with tab_dash:
    dashboard_tab()

with tab_chat:
    chatbot_tab()

with tab_email:
    email_tab()
