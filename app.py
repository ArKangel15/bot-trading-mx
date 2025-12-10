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

st.title("📈 Bot de Trading — Acciones Mexicanas")
st.write("Análisis técnico con MACD + Bollinger + KDJ")

# Analizar todas las acciones
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
# TARJETAS MODELO BLOOMBERG
# =============================
st.subheader("📊 Análisis Individual por Acción")

for i, fila in tabla.iterrows():
    st.markdown(
        f"""
        <div style="background:#FFF; padding:20px; border-radius:15px; 
                    border:1px solid #e3e3e3; margin-bottom:20px;">

            <h2>📌 {fila['Ticker']} — 
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
        """,
        unsafe_allow_html=True
    )


