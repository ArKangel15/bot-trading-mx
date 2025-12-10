import streamlit as st
import pandas as pd
from bot_trading import analizar, acciones

# ================================
# CONFIGURACIÓN DE LA PÁGINA
# ================================
st.set_page_config(page_title="Bot de Trading MX", layout="wide")

# ================================
# TÍTULO PRINCIPAL
# ================================
st.title("📈 Bot de Trading — Acciones Mexicanas")
st.write("Análisis técnico con MACD + Bollinger + KDJ + RSI + EMAs")

# ================================
# ANALIZAR TODAS LAS ACCIONES
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
# TARJETAS ESTILO BLOOMBERG
# ================================
st.subheader("📊 Análisis Individual por Acción")

for i, fila in tabla.iterrows():

    st.markdown(
        f"""
        <div style="
            background-color:#ffffff;
            padding:25px;
            border-radius:20px;
            margin-bottom:25px;
            border:1px solid #dcdde1;
            box-shadow:0px 2px 8px rgba(0,0,0,0.05);
        ">

            <!-- TÍTULO -->
            <h2 style="margin:0; font-size:28px;">
                📌 <strong>{fila['Ticker']}</strong> — 
                <span style="color:#0066ff;">{fila['Señal Final']}</span>
            </h2>

            <!-- PRECIO -->
            <p style="font-size:18px; margin-top:10px;">
                <strong>Precio:</strong> {fila['Precio']}
            </p>

            <!-- INDICADORES PRINCIPALES -->
            <h3 style="margin-top:15px;">Indicadores principales</h3>
            <p>
                <strong>MACD:</strong> {fila['MACD Señal']} <br>
                <strong>KDJ:</strong> {fila['KDJ Señal']} <br>
                <strong>Bollinger:</strong> {fila['Bollinger Señal']}
            </p>

            <!-- INDICADORES ADICIONALES -->
            <h3 style="margin-top:25px;">🔍 Indicadores adicionales</h3>

            <p>
                <strong>RSI (14):</strong> {fila['RSI']} — 
                {"🟢 Normal" if fila['RSI Estado']=="Normal"
                    else "🔴 Sobrecompra" if fila['RSI Estado']=="Sobrecompra"
                    else "🟡 Sobreventa"}
            </p>

            <p>
                <strong>Tendencia EMA50 / EMA200:</strong>
                {"🟢 Alcista (EMA50 > EMA200)" if fila['Tendencia']=="Alcista"
                    else "🔴 Bajista (EMA50 < EMA200)"}
            </p>

            <p>
                <strong>Precio vs EMA50:</strong>
                {"🟢 Precio arriba de EMA50" if fila['Precio EMA50']=="Arriba"
                    else "🔴 Precio debajo de EMA50"}
            </p>

            <!-- RANGOS BOLLINGER -->
            <h3 style="margin-top:25px;">📏 Rangos Bollinger</h3>
            <p>
                <strong>Banda Superior:</strong> {fila['Banda Superior']} <br>
                <strong>Banda Inferior:</strong> {fila['Banda Inferior']}
            </p>

            <!-- EXPLICACIÓN COMPLETA -->
            <h3 style="margin-top:25px;">📝 Explicación completa</h3>
            <p style="font-size:16px;">
                {fila['Explicación']}
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )
