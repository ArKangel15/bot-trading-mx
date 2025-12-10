import streamlit as st
import pandas as pd
from bot_trading import analizar, acciones

st.set_page_config(page_title="Bot Trading MX", layout="wide")

# Forzar modo claro
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background-color: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Bot de Trading — Acciones Mexicanas")


# ---------------------
#   ANALIZAR ACCIONES
# ---------------------
resultados = []
for acc in acciones:
    r = analizar(acc)
    if r:
        resultados.append(r)

tabla = pd.DataFrame(resultados)

st.subheader("📊 Tabla General")
st.dataframe(tabla, use_container_width=True)

# ---------------------
#   TARJETAS INDIVIDUALES
# ---------------------
st.subheader("📊 Análisis Individual por Acción")

for i, fila in tabla.iterrows():

    ticker = fila["Ticker"]
    precio = fila["Precio"]
    macd_s = fila["MACD Señal"]
    boll_s = fila["Bollinger Señal"]
    kdj_s = fila["KDJ Señal"]
    banda_sup = fila["Banda Superior"]
    banda_inf = fila["Banda Inferior"]
    explic = fila["Explicación"]
    señal_final = fila["Señal Final"]

    html = f"""
    <div style="
        background:white;
        padding:25px;
        border-radius:15px;
        border:1px solid #dcdcdc;
        margin-bottom:25px;
        box-shadow:0 2px 6px rgba(0,0,0,0.1);
    ">
        <h2>
            📌 <strong>{ticker}</strong>
            — <span style="color:#0066cc;">{señal_final}</span>
        </h2>

        <p><strong>Precio:</strong> {precio}</p>

        <h3>Indicadores</h3>
        <p><strong>MACD:</strong> {macd_s}</p>
        <p><strong>Bollinger:</strong> {boll_s}</p>
        <p><strong>KDJ:</strong> {kdj_s}</p>

        <h3>Niveles</h3>
        <p><strong>Banda Superior:</strong> {banda_sup}</p>
        <p><strong>Banda Inferior:</strong> {banda_inf}</p>

        <h3>Explicación</h3>
        <p>{explic}</p>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)
