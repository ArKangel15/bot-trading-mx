import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from bot_trading import analizar, acciones

st.set_page_config(page_title="Bot de Trading MX", layout="wide")

st.title("📈 Bot de Trading — Acciones Mexicanas")
st.write("Análisis técnico con MACD + Bollinger + KDJ + RSI + EMAs")

# Analizar acciones
resultados = []
for acc in acciones:
    r = analizar(acc)
    if r:
        resultados.append(r)

tabla = pd.DataFrame(resultados)

st.subheader("📊 Resultados del Análisis Técnico")
st.dataframe(tabla, use_container_width=True)

st.download_button(
    label="📥 Descargar CSV",
    data=tabla.to_csv(index=False),
    file_name="resultados_trading.csv",
    mime="text/csv"
)

# ==========================
# TARJETAS HTML SIN RESTRICCIÓN
# ==========================
st.subheader("📊 Análisis Individual por Acción — HTML REAL")

for _, fila in tabla.iterrows():

    # Color del MACD
    macd_color = "🟢" if fila["MACD Señal"] == "MACD Alcista" else "🔴"
     
    html = f"""
    <div style="
        background-color:#ffffff;
        padding:25px;
        border-radius:20px;
        margin-bottom:25px;
        border:1px solid #cccccc;
        font-family:Arial;
    ">

        <h2 style="margin:0; font-size:26px;">
            📌 <strong>{fila['Ticker']}</strong> —
            <span style="color:#0066ff;">{fila['Señal Final']}</span>
        </h2>

        <p style="font-size:18px; margin-top:10px;">
            💲 <strong>Precio actual:</strong> {fila['Precio']}
        </p>



    </div>
    """

    components.html(html, height=200)




