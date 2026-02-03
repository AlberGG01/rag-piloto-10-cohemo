"""
Dashboard de métricas del RAG
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import sys

# Añadir root path para importar módulos correctamente si se corre desde pages/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.observability import get_observer

st.set_page_config(page_title="RAG Metrics", page_icon="📊", layout="wide")

st.title("📊 RAG Observability Dashboard")

observer = get_observer()

# Layout de filtros
with st.sidebar:
    st.header("Configuración")
    n_queries = st.slider("Últimas N queries", 10, 500, 100)
    if st.button("🔄 Refrescar Datos"):
        st.rerun()

# Cargar logs
if not observer.log_file.exists():
    st.warning("No hay logs disponibles aún. Ejecuta algunas queries primero.")
    st.stop()

data = []
try:
    with open(observer.log_file, "r", encoding="utf-8") as f:
        # Leer línea por línea para evitar errores de JSON inválido en una línea
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
except Exception as e:
    st.error(f"Error leyendo logs: {e}")
    st.stop()

if not data:
    st.info("Log file vacío.")
    st.stop()

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

# Filtrar últimas N
df = df.tail(n_queries)

# ========== MÉTRICAS PRINCIPALES ==========
st.header("📈 Métricas Globales")

metrics = observer.get_metrics_summary(last_n=n_queries)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Queries",
        metrics.get("total_queries", 0)
    )

with col2:
    st.metric(
        "Latencia P95",
        f"{metrics.get('p95_latency', 0):.2f}s"
    )

with col3:
    st.metric(
        "Coste Total",
        f"${metrics.get('total_cost', 0):.2f}"
    )

with col4:
    st.metric(
        "Validation Pass Rate",
        f"{metrics.get('validation_pass_rate', 0):.1f}%"
    )

st.divider()

# ========== GRÁFICOS ==========

# Latencia en el tiempo
st.subheader("⏱️ Latencia por Query")
if not df.empty and 'latency_total' in df.columns:
    fig_latency = px.line(
        df,
        x='timestamp',
        y='latency_total',
        title="Latencia Total (segundos)",
        markers=True,
        hover_data=['query']
    )
    if 'avg_latency' in metrics:
        fig_latency.add_hline(
            y=metrics.get('avg_latency', 0),
            line_dash="dash",
            annotation_text="Promedio"
        )
    st.plotly_chart(fig_latency, use_container_width=True)

# Distribución de latencias por componente
st.subheader("🔍 Desglose de Latencia Promedio")
cols_lat = ['latency_retrieval', 'latency_generation', 'latency_validation']
breakdown_data = {}
for c in cols_lat:
    if c in df.columns:
        breakdown_data[c.replace('latency_', '').title()] = df[c].mean()

if breakdown_data:
    fig_breakdown = go.Figure(data=[
        go.Bar(
            x=list(breakdown_data.keys()),
            y=list(breakdown_data.values()),
            text=[f"{v:.2f}s" for v in breakdown_data.values()],
            textposition='auto'
        )
    ])
    fig_breakdown.update_layout(title="Latencia Promedio por Componente (s)")
    st.plotly_chart(fig_breakdown, use_container_width=True)

# Confianza vs Validación
st.subheader("🎯 Calidad de Respuesta")
col1, col2 = st.columns(2)

with col1:
    if 'confidence' in df.columns:
        fig_confidence = px.histogram(
            df,
            x='confidence',
            nbins=20,
            title="Distribución de Confidence Score",
            labels={'confidence': 'Confidence Score (%)'}
        )
        st.plotly_chart(fig_confidence, use_container_width=True)

with col2:
    if 'validation_passed' in df.columns:
        validation_counts = df['validation_passed'].value_counts()
        fig_validation = px.pie(
            values=validation_counts.values,
            names=["Pass" if k else "Fail" for k in validation_counts.index],
            title="Tasa de Validación",
            color_discrete_map={"Pass": "green", "Fail": "red"}
        )
        st.plotly_chart(fig_validation, use_container_width=True)

# Costes acumulados
st.subheader("💰 Evolución de Costes")
if 'cost_usd' in df.columns:
    df['cost_cumsum'] = df['cost_usd'].cumsum()
    fig_cost = px.line(
        df,
        x='timestamp',
        y='cost_cumsum',
        title="Coste Acumulado (USD)",
        labels={'cost_cumsum': 'Coste Acumulado ($)'}
    )
    st.plotly_chart(fig_cost, use_container_width=True)

# Tabla de queries recientes
st.subheader("📋 Detalle de Queries")
cols_view = ['timestamp', 'query', 'latency_total', 'confidence', 'validation_passed', 'cost_usd']
# Filter only columns that exist
cols_view = [c for c in cols_view if c in df.columns]

st.dataframe(
    df[cols_view].sort_values('timestamp', ascending=False),
    use_container_width=True
)
