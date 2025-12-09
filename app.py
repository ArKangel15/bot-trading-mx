import streamlit as st
import pandas as pd
from bot_trading import analizar, acciones

st.set_page_config(page_title="Bot de Trading MX", layout="wide")

st.title("📈 Bot de Trading — Acciones Mexicanas")
st.write("Análisis técnico con MACD + Bollinger + KDJ")

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


st.subheader("📊 Análisis por Acción (Estilo Bloomberg)")

for idx, row in tabla.iterrows():
    st.markdown(
        f"""
        <div style="
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
        ">
            <h3 style="margin: 0; padding:0;">📈 {row['Ticker']} — <span style="color:#0073e6">{row['Señal Final']}</span></h3>
            <p><strong>Precio actual:</strong> {row['Precio']}</p>
            <p><strong>MACD:</strong> {row['MACD Señal']}</p>
            <p><strong>KDJ:</strong> {row['KDJ Señal']}</p>
            <p><strong>Bollinger:</strong> {row['Bollinger Señal']}</p>
            <p><strong>📝 Explicación completa:</strong> {row['Explicación']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
