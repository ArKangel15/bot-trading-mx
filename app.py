import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import textwrap
from datetime import datetime
import pytz

from bot_trading import (
    descargar_batch,
    analizar_con_data,
    acciones_mx,
    acciones_usa,
)

# ==========================
# CONFIGURACIÓN GENERAL
# ==========================
st.markdown('<div id="top"></div>', unsafe_allow_html=True)
st.set_page_config(page_title="Trading by Arkangel", layout="wide")

st.title("📈 Trading de Acciones by Arkangel")
st.write("Análisis técnico con MACD + Bollinger + KDJ + RSI + EMAs + ATR")

# ==========================
# SELECCIÓN DE MERCADO
# ==========================
mercado = st.selectbox(
    "📍 Selecciona mercado",
    ["México (BMV)", "Estados Unidos (USA)"],
    index=0
)

acciones = acciones_mx if mercado == "México (BMV)" else acciones_usa
st.caption(f"Analizando: {len(acciones)} acciones — {mercado}")

# ==========================
# DESCARGA DE DATOS
# ==========================
batch = descargar_batch(acciones, period="2y", interval="1d")
tz_mx = pytz.timezone("America/Mazatlan")
batch_ts = datetime.now(tz_mx).strftime("%Y-%m-%d %H:%M:%S")

resultados = []
faltantes = []

for t in acciones:
    try:
        if isinstance(batch.columns, pd.MultiIndex):
            if t not in batch.columns.get_level_values(0):
                faltantes.append(t)
                continue
            df_t = batch[t].copy()
        else:
            df_t = batch.copy()

        r = analizar_con_data(t, df_t)
        if r:
            resultados.append(r)
        else:
            faltantes.append(t)

    except Exception:
        faltantes.append(t)

st.caption(
    f"Total: {len(acciones)} | OK: {len(resultados)} | "
    f"Faltantes: {len(faltantes)} | Datos del: {batch_ts}"
)

tabla = pd.DataFrame(resultados)

# ==========================
# SCORE + SEMÁFORO FINAL
# ==========================
def calcular_score_y_semaforo(row):
    score = 0

    score += 1 if row["MACD"] > row["Signal"] else -1

    rsi = float(row["RSI"])
    if rsi < 30:
        score += 1
    elif rsi > 70:
        score -= 1

    boll = row["Bollinger Señal"]
    if boll == "Sobreventa":
        score += 1
    elif boll == "Sobrecompra":
        score -= 1

    score += 1 if row["Tendencia"] == "Alcista" else -1
    score += 1 if row["Precio EMA50"] == "Arriba" else -1
    score += 1 if row["K"] > row["D"] else -1

    if score >= 4:
        sem = "🟢 COMPRA FUERTE"
    elif score >= 2:
        sem = "🟢 POSIBLE COMPRA"
    elif score <= -4:
        sem = "🔴 VENTA FUERTE"
    elif score <= -2:
        sem = "🔴 POSIBLE VENTA"
    else:
        sem = "🟡 ESPERAR"

    return score, sem


tabla["Score"] = ""
tabla["Semáforo Final"] = ""

for i in range(len(tabla)):
    sc, sem = calcular_score_y_semaforo(tabla.iloc[i])
    tabla.at[i, "Score"] = sc
    tabla.at[i, "Semáforo Final"] = sem

# ==========================
# SEMÁFORO ATR
# ==========================
def semaforo_atr(atr_pct):
    try:
        atr_pct = float(atr_pct)
    except:
        return "—"

    if atr_pct < 1:
        return "⚪ MUY LENTA"
    elif atr_pct <= 3:
        return "🟢 VOLATILIDAD SANA"
    elif atr_pct <= 4:
        return "🟡 VOLATIL"
    else:
        return "🔴 MUY VOLATIL"

tabla["Semáforo ATR"] = tabla["ATR%"].apply(semaforo_atr)

# ==========================
# ORDEN PARA RESUMEN
# ==========================
orden_semaforo = {
    "🟢 COMPRA FUERTE": 1,
    "🟢 POSIBLE COMPRA": 2,
    "🟡 ESPERAR": 3,
    "🔴 POSIBLE VENTA": 4,
    "🔴 VENTA FUERTE": 5
}

orden_atr = {
    "🟢 VOLATILIDAD SANA": 1,
    "🟡 VOLATIL": 2,
    "🔴 MUY VOLATIL": 3,
    "⚪ MUY LENTA": 4,
    "—": 99
}

tabla["orden_resumen"] = tabla["Semáforo Final"].map(orden_semaforo).fillna(99)
tabla["orden_atr"] = tabla["Semáforo ATR"].map(orden_atr).fillna(99)

tabla_resumen = tabla.sort_values(
    ["orden_resumen", "orden_atr"],
    ascending=[True, True]
)

# ==========================
# 🔎 BUSCADOR RESUMEN
# ==========================
st.markdown('<div id="resumen"></div>', unsafe_allow_html=True)
st.subheader("📌 Resumen rápido (toca la acción para ir a su tarjeta)")

busqueda = st.text_input(
    "🔎 Buscar acción (ticker)",
    placeholder="Ejemplo: WALMEX, AAPL, NVDA"
).upper().strip()

tabla_filtrada = tabla_resumen.copy()
if busqueda:
    tabla_filtrada = tabla_filtrada[
        tabla_filtrada["Ticker"].str.contains(busqueda, case=False, na=False)
    ]

items = []

for _, fila in tabla_filtrada.iterrows():
    anchor_id = fila["Ticker"].replace(".", "-")

    item_html = textwrap.dedent(f"""
    <div style="padding:8px 0; border-bottom:1px solid #eee;">
      🔗 <a href="javascript:void(0)"
        onclick="goToTicker('{anchor_id}')"
        style="font-weight:800; color:#0066ff;">
        {fila["Ticker"]}
      </a>
      &nbsp; — &nbsp;
      <strong>{fila["Semáforo Final"]}</strong>
      &nbsp; | &nbsp;
      💲 {fila["Precio"]}
      &nbsp; | &nbsp;
      🧱 {fila["Soporte Estadístico"]}
      &nbsp; | &nbsp;
      ⚖️ {fila["Precio Medio"]}
      &nbsp; | &nbsp;
      🏁 {fila["Zona Cara"]}
      &nbsp; | &nbsp;
      Score: {fila["Score"]}/6
      &nbsp; — &nbsp;
      <strong>{fila["Semáforo ATR"]}</strong>
      &nbsp; — &nbsp;
      <strong>RIESGO {fila["Riesgo%"]}%</strong>
    </div>
    """).strip()

    items.append(item_html)

resumen_html = f"""
<div style="background:#fff; padding:16px; border-radius:16px; border:1px solid #ddd;">
<script>
function goToTicker(id) {{
  const doc = window.parent.document;
  const el = doc.getElementById(id);
  if (el) {{
    el.scrollIntoView({{ behavior: "smooth", block: "start" }});
  }}
}}
</script>
{''.join(items)}
</div>
"""

components.html(resumen_html, height=600, scrolling=True)

# ==========================
# TABLA GENERAL + DESCARGA
# ==========================
st.subheader("📊 Resultados del Análisis Técnico")
st.dataframe(tabla, use_container_width=True)

st.download_button(
    "📥 Descargar CSV",
    tabla.to_csv(index=False),
    "resultados_trading.csv",
    "text/csv"
)

# ==========================
# TARJETAS INDIVIDUALES
# ==========================
st.subheader("📊 Análisis Individual por Acción")

for _, fila in tabla.iterrows():
    anchor_id = fila["Ticker"].replace(".", "-")
    st.markdown(
        f'<div id="{anchor_id}" style="position:relative; top:-80px;"></div>',
        unsafe_allow_html=True
    )

    components.html(
        f"""
        <div style="background:#fff; padding:25px; border-radius:20px;
        margin-bottom:25px; border:1px solid #ccc; font-family:Arial;">
        <h2>📌 {fila["Ticker"]} — {fila["Semáforo Final"]}</h2>
        <p><strong>Precio:</strong> {fila["Precio"]}</p>
        <p><strong>Score:</strong> {fila["Score"]}/6</p>
        <p><strong>ATR:</strong> {fila["Semáforo ATR"]}</p>
        </div>
        """,
        height=220
    )
