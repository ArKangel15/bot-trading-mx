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
    # Color del MACD (basado en números, no en texto)
    macd_val = float(fila["MACD"])
    signal_val = float(fila["Signal"])
    macd_color = "🟢" if macd_val > signal_val else "🔴"

    rsi_val = float(fila["RSI"])
    rsi_estado = str(fila["RSI Estado"])
    # Semáforo RSI
    rsi_color = "🟢" if rsi_estado == "Normal" else ("🔴" if rsi_estado == "Sobrecompra" else "🟡")


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

        <h3 style="margin-top:20px;">📉 MACD</h3>
        <p style="font-size:17px;">
        {macd_color} <strong>{fila['MACD Señal']}</strong><br>
        <strong>MACD:</strong> {fila['MACD']}<br>
        <strong>Signal:</strong> {fila['Signal']}
        </p>

        <h3 style="margin-top:20px;">📊 RSI (14)</h3>
        <p style="font-size:17px;">
        {rsi_color} <strong>{rsi_estado}</strong><br>
        <strong>RSI:</strong> {rsi_val:.2f}<br>
        <small>Rangos: <b>Sobreventa</b> &lt; 30 | <b>Normal</b> 30–70 | <b>Sobrecompra</b> &gt; 70</small>
        </p>

        
    </div>
    """

    components.html(html, height=360)

