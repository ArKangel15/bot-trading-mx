import streamlit as st
import pandas as pd
from bot_trading import analizar, acciones

# ================================
# CONFIGURACIÓN
# ================================
st.set_page_config(page_title="Bot de Trading MX", layout="wide")

# ================================
# TÍTULO PRINCIPAL
# ================================
st.title("📈 Bot de Trading — Acciones Mexicanas")
st.write("Análisis técnico con MACD + Bollinger + KDJ + RSI + EMAs")

# ================================
# ANALIZA TODAS LAS ACCIONES
# ================================
resultados = []
for acc in acciones:
    r = analizar(acc)
    if r:
        resultados.append(r)

tabla = pd.DataFrame(resultados)

# ================================
# TABLA PRINCIPAL
# ================================
st.subheader("📊 Resultados del Análisis Técnico")
st.dataframe(tabla, use_container_width=True)

# DESCARGA CSV
st.download_button(
    label="📥 Descargar CSV",
    data=tabla.to_csv(index=False),
    file_name="resultados_trading.csv",
    mime="text/csv"
)

# ================================
# TARJETAS ESTILO BLOOMBERG (PRUEBA)
# ================================
st.subheader("📊 Análisis Individual por Acción — PRUEBA")

for _, fila in tabla.iterrows():

    st.markdown(
        f"""
        <div style="
            background-color:#ffffff;
            padding:20px;
            border-radius:15px;
            margin-bottom:20px;
            border:1px solid #cccccc;
            font-size:22px;
        ">
            📌 <strong>{fila['Ticker']}</strong> — 
            <span style="color:#0066ff;">{fila['Señal Final']}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
