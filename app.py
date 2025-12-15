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
st.subheader("📊 Análisis Individual por Acción")

for _, fila in tabla.iterrows():
    # Color del MACD (basado en números, no en texto)
    macd_val = float(fila["MACD"])
    signal_val = float(fila["Signal"])
    macd_color = "🟢" if macd_val > signal_val else "🔴"

   # RSI semáforo por acción (🟢 comprar | 🟡 esperar | 🔴 vender)
    rsi_val = float(fila["RSI"])
    if rsi_val < 30:
        rsi_estado = "Sobreventa"
        rsi_color = "🟢"   # Comprar
    elif rsi_val <= 70:
        rsi_estado = "Normal"
        rsi_color = "🟡"   # Esperar
    else:
        rsi_estado = "Sobrecompra"
        rsi_color = "🔴"   # Vender

        # ===== Semáforo EMAs =====
    tendencia = str(fila["Tendencia"])          # "Alcista" o "Bajista"
    precio_ema50 = str(fila["Precio EMA50"])    # "Arriba" o "Debajo"

    ema_trend_color = "🟢" if tendencia == "Alcista" else "🔴"
    precio_ema50_color = "🟢" if precio_ema50 == "Arriba" else "🔴"

    ema50_val = float(fila["EMA50"])
    ema200_val = float(fila["EMA200"])

    # ===== Semáforo Bollinger (acción) =====
    boll_estado = str(fila["Bollinger Señal"])  # "Sobreventa", "Normal", "Sobrecompra"

    if boll_estado == "Sobreventa":
        boll_color = "🟢"   # Comprar
    elif boll_estado == "Normal":
        boll_color = "🟡"   # Esperar
    else:  # "Sobrecompra"
        boll_color = "🔴"   # Vender

    
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
         RSI: {rsi_val:.2f}<br>
        Rangos: Sobreventa &lt; 30 | Normal 30–70 | Sobrecompra &gt; 70
        </p>

        <h3 style="margin-top:20px;">📉 Bollinger (Volatilidad)</h3>
        <p style="font-size:17px;">
            {boll_color} <strong>Estado:</strong> {boll_estado}<br>
            <strong>Banda Superior:</strong> {fila['Banda Superior']}<br>
            <strong>Banda Inferior:</strong> {fila['Banda Inferior']}<br>
            <small>
                Interpretación: 🟢 precio bajo banda inferior (zona compra) |
                🟡 dentro del canal (esperar) |
                🔴 sobre banda superior (zona venta)
            </small>
        </p>
    
        <h3 style="margin-top:20px;">📈 Tendencia (EMAs)</h3>
        <p style="font-size:17px;">
            {ema_trend_color} <strong>EMA50 vs EMA200:</strong> {tendencia}<br>
            <strong>EMA50:</strong> {ema50_val:.2f}<br>
            <strong>EMA200:</strong> {ema200_val:.2f}
        </p>

        <h3 style="margin-top:15px;">⏱️ Reacción (Precio vs EMA50)</h3>
        <p style="font-size:17px;">
            {precio_ema50_color} <strong>Precio vs EMA50:</strong> {precio_ema50}
        </p>

        
    </div>
    """

    components.html(html, height=700)














