import streamlit as st
import pandas as pd
from bot_trading import analizar, acciones

st.set_page_config(page_title="Bot de Trading MX", layout="wide")

# Forzar modo claro
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# Título principal
st.title("📈 Bot de Trading — Acciones Mexicanas")
st.write("Análisis técnico con MACD + Bollinger + KDJ")

# Analizar acciones
resultados = []
for acc in acciones:
    r = analizar(acc)
    if r:
        resultados.append(r)

tabla = pd.DataFrame(resultados)

# =============================
# TABLA COMPLETA
# =============================
st.subheader("📊 Tabla General de Señales")
st.dataframe(tabla, use_container_width=True)

st.download_button(
    "📥 Descargar CSV",
    tabla.to_csv(index=False),
    "resultados.csv",
    "text/csv"
)

# =============================
# TARJETAS INDIVIDUALES
# =============================
st.subheader("📊 Análisis Individual por Acción")

for i, fila in tabla.iterrows():

    html_card = f"""
    <div style="
        background:white;
        padding:25px;
        border-radius:15px;
        border:1px solid #dcdcdc;
        margin-bottom:25px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
    ">

        <h2 style="margin:0; font-size:28px;">
            📌 <strong>{fila['Ticker']}</strong> — 
            <span style="color:#0066cc;">{fila['Señal Final']}</span>
        </h2>

        <p style="font-size:18px; margin-top:10px;">
            <strong>Precio:</strong> {fila['Precio']}
        </p>

        <h3>📘 Indicadores</h3>
        <p><strong>MACD:</strong> {fila['MACD Señal']}</p>
        <p><strong>Bollinger:</strong> {fila['Bollinger Señal']}</p>
        <p><strong>KDJ:</strong> {fila['KDJ Señal']}</p>

        <h3>📏 Niveles</h3>
        <p><strong>Banda Superior:</strong> {fila['Banda Superior']}</p>
        <p><strong>Banda Inferior:</strong> {fila['Banda Inferior']}</p>

        <h3>📝 Explicación</h3>
        <p>{fila['Explicación']}</p>

    </div>
    """

    st.markdown(html_card, unsafe_allow_html=True)
