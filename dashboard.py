"""
dashboard.py
Capa de Usabilidad: Dashboard en Streamlit.
Muestra KPIs del día, historial de telemetría y boletines semanales
del Asesor Inteligente del Vivero CECAR.
"""

import streamlit as st
import pandas as pd
from database import get_connection, init_db

st.set_page_config(page_title="Asesor Vivero CECAR", page_icon="🌱", layout="wide")

init_db()  # asegura que las tablas existan aunque sea la primera vez que corre

st.title("🌱 Asesor Inteligente - Vivero CECAR")
st.caption("Monitoreo climático y recomendaciones de riego en tiempo real")

conn = get_connection()
df = pd.read_sql_query(
    "SELECT * FROM telemetria_diaria ORDER BY fecha_registro DESC", conn
)
boletines = pd.read_sql_query(
    "SELECT * FROM boletines_semanales ORDER BY fecha_generacion DESC", conn
)
conn.close()

if df.empty:
    st.warning("Todavía no hay datos guardados. Corre `python main_diario.py` primero.")
else:
    ultimo = df.iloc[0]

    # --- KPIs del último registro ---
    st.subheader("📊 Estado Actual")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Temperatura", f"{ultimo['temperatura_c']} °C")
    col2.metric("Precipitación", f"{ultimo['precipitacion_mm']} mm")
    col3.metric("Humedad", f"{ultimo['humedad_relativa_pct']} %")
    col4.metric("Ráfaga de viento", f"{ultimo['rafaga_viento_kmh']} km/h")
    col5.metric("Orden de riego", ultimo["orden_riego"])

    if ultimo["alerta"]:
        st.error(f"🚨 {ultimo['mensaje']}")
    else:
        st.success(f"✅ {ultimo['mensaje']}")

    st.divider()

    # --- Gráficas de historial ---
    st.subheader("📈 Historial de Telemetría")
    df_grafica = df.sort_values("fecha_registro").set_index("fecha_registro")

    col_izq, col_der = st.columns(2)
    with col_izq:
        st.line_chart(df_grafica["temperatura_c"], color="#FF4B4B")
        st.caption("Temperatura (°C)")
    with col_der:
        st.bar_chart(df_grafica["precipitacion_mm"], color="#1E90FF")
        st.caption("Precipitación (mm)")

    st.divider()

    # --- Tabla completa ---
    st.subheader("🗂️ Registros Completos")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # --- Boletines semanales ---
    st.subheader("📰 Boletines Climáticos Semanales")
    if boletines.empty:
        st.info("Aún no se ha generado ningún boletín. Corre `python ai_agent.py`.")
    else:
        for _, fila in boletines.iterrows():
            with st.expander(f"Boletín del {fila['fecha_inicio']} al {fila['fecha_fin']}"):
                st.write(fila["contenido"])