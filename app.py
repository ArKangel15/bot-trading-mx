import streamlit as st
import pandas as pd
from bot_trading import analizar, acciones
import streamlit.components.v1 as components

st.set_page_config(page_title="Bot Trading MX", layout="wide")

st.title("📈 Bot de Trading — Acciones Mexicanas")

# --- Cargar análisis ---
resultados = [analizar(acc) for acc in acciones if analizar(acc)]
tabla = pd.DataFrame(resultados)

st.subheader("📊 Resultados del Análisis Técnico")
st.dataframe(tabla, use_container_width=True)

st.download_button("📥 Descargar CSV", data=tabla.to_csv(index=False),
                   file_name="resultados_trading.csv", mime="text/csv")

# --- Tarjetas con HTML REAL usando components.html ---
st.subheader("📊 Análisis Individual por Acción")

for _, fila in tabla.iterrows():

    html = f"""
    <div style="
        background:white;
        padding:25px;
        border-radius:15px;
        border:1px solid #dcdcdc;
        margin-bottom:25px;
        box-shadow:0 2px 6px rgba(0,0,0,0.1);
    ">

        <h2 style="margin:0;">
            📌 <strong>{fila['Ticker']}</strong> —
            <span style="color:#0066cc;">{fila['Señal Final']}</span>
        </h2>

        <p><strong>Precio:</strong> {fila['Precio']}</p>

        <h3>Indicadores</h3>
        <p><strong>MACD:</strong> {fila['MACD Señal']}</p>
        <p><strong>Bollinger:</strong> {fila['Bollinger Señal']}</p>
        <p><strong>KDJ:</strong> {fila['KDJ Señal']}</p>

        <h3>Niveles</h3>
        <p><strong>Banda Superior:</strong> {fila['Banda Superior']}</p>
        <p><strong>Banda Inferior:</strong> {fila['Banda Inferior']}</p>

        <h3>Explicación</h3>
        <p>{fila['Explicación']}</p>

    </div>
    """

    components.html(html, height=500)
