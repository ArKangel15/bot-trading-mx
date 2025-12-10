import streamlit as st
import pandas as pd
from bot_trading import analizar, acciones

# Forzar modo claro
st.set_page_config(page_title="Bot de Trading MX", layout="wide")
st.markdown(
    """
    <style>
    @media (prefers-color-scheme: dark) {
        html, body, [data-testid="stAppViewContainer"] {
            background-color: white !important;
            color: black !important;
        }
        .stCard, .stDataFrame, .stTable, .element-container {
            background-color: white !important;
            color: black !important;
        }
        h1, h2, h3, h4, h5, h6, p, div {
            color: black !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📈 Bot de Trading — Acciones Mexicanas")
st.write("Análisis técnico con MACD + Bollinger + KDJ")

# Obtener datos
resultados = []
for acc in acciones:
    r = analizar(acc)
    if r:
        resultados.append(r)

tabla = pd.DataFrame(resultados)

# =============================
# TABLA GRANDE COMPLETA
# =============================
st.subheader("📊 Resultados del Análisis Técnico")
st.dataframe(tabla, use_container_width=True)

st.download_button(
    label="📥 Descargar CSV",
    data=tabla.to_csv(index=False),
    file_name="resultados_trading.csv",
    mime="text/csv"
)


# =============================
# TARJETAS BLOOMBERG COMPATIBLES
# =============================
st.subheader("📊 Análisis por Acción (Estilo Bloomberg)")

for i, fila in tabla.iterrows():

    st.markdown(
        f"""
        <div style="background-color:#ffffff; padding:25px; border-radius:20px; margin-bottom:25px; 
                    border:1px solid #dfe6e9;">

            <h2 style="margin:0; font-size:28px;">
                📈 <strong>{fila['Ticker']}</strong> — 
                <span style="color:#0066ff;">{fila['Señal Final']}</span>
            </h2>

            <p style="font-size:18px; margin-top:10px;">
                <strong>Precio actual:</strong> {fila['Precio']}
            </p>

            <!-- INDICADORES CLÁSICOS -->
            <h3>📌 Indicadores clave</h3>
            <p>
                <strong>MACD:</strong> {fila['MACD Señal']} <br>
                <strong>KDJ:</strong> {fila['KDJ Señal']} <br>
                <strong>Bollinger:</strong> {fila['Bollinger Señal']}
            </p>

            <!-- RANGOS -->
            <h3>📏 Niveles técnicos</h3>
            <p>
                <strong>Banda inferior:</strong> {fila['Banda Inferior']} <br>
                <strong>Banda superior:</strong> {fila['Banda Superior']} 
            </p>

            <h3>📝 Explicación completa</h3>
            <p>{fila['Explicación']}</p>

        </div>
        """,
        unsafe_allow_html=True
    )
