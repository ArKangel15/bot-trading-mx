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

def calcular_score_y_semaforo(row):
    score = 0

    # MACD
    macd_val = float(row["MACD"])
    signal_val = float(row["Signal"])
    score += 1 if macd_val > signal_val else -1

    # RSI
    rsi_val = float(row["RSI"])
    if rsi_val < 30:
        score += 1
    elif rsi_val > 70:
        score -= 1

    # Bollinger
    boll = str(row["Bollinger Señal"])
    if boll == "Sobreventa":
        score += 1
    elif boll == "Sobrecompra":
        score -= 1

    # Tendencia (EMA50 vs EMA200)
    tendencia = str(row["Tendencia"])
    score += 1 if tendencia == "Alcista" else -1

    # Precio vs EMA50
    precio_ema50 = str(row["Precio EMA50"])
    score += 1 if precio_ema50 == "Arriba" else -1

    # KDJ
    K_val = float(row["K"])
    D_val = float(row["D"])
    score += 1 if K_val > D_val else -1

    # Semáforo final por score
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

def semaforo_atr(atr_pct):
    try:
        atr_pct = float(atr_pct)
    except:
        return "—"

    if atr_pct < 1:
        return "⚪ Muy lenta"
    elif atr_pct <= 3:
        return "🟢 Volatilidad sana"
    elif atr_pct <= 4:
        return "🟡 Volátil"
    else:
        return "🔴 Muy volátil"

tabla["Semáforo ATR"] = tabla["ATR%"].apply(semaforo_atr)


# Orden de prioridad para el resumen
orden_semaforo = {
    "🟢 COMPRA FUERTE": 1,
    "🟢 POSIBLE COMPRA": 2,
    "🟡 ESPERAR": 3,
    "🔴 POSIBLE VENTA": 4,
    "🔴 VENTA FUERTE": 5
}

# Crear columna auxiliar solo para ordenar
tabla["orden_resumen"] = tabla["Semáforo Final"].map(orden_semaforo)

# Tabla ordenada SOLO para el resumen
tabla_resumen = tabla.sort_values("orden_resumen")

# ==========================
# RESUMEN RÁPIDO SUPERIOR
# ==========================
import textwrap

# ... tu código arriba ...
st.markdown('<div id="resumen"></div>', unsafe_allow_html=True)
st.subheader("📌 Resumen rápido (toca el ticker para ir a su tarjeta)")

items = []
#for _, fila in tabla.iterrows():
for _, fila in tabla_resumen.iterrows():
    anchor_id = str(fila["Ticker"]).replace(".", "-")
   
    item_html = textwrap.dedent(f"""
<div style="padding:8px 0; border-bottom:1px solid #eee;">

🔗 <a href="javascript:void(0)"
        onclick="goToTicker('{anchor_id}')"
        style="text-decoration:none; font-weight:800; color:#0066ff;">
    {fila["Ticker"]}
  </a> 
  
  &nbsp; — &nbsp;
  <span style="font-weight:800;">{fila["Semáforo Final"]}</span>
  &nbsp; | &nbsp;
  <span style="color:#666;">Score: {fila.get("Score","–")}/6</span>
  &nbsp; — &nbsp;
  <span style="font-weight:800;">{fila["Semáforo ATR"]}</span>
</div>
""").strip()

    items.append(item_html)

resumen_html = textwrap.dedent(f"""
<div style="
  background-color:#ffffff;
  padding:16px;
  border-radius:16px;
  border:1px solid #dcdcdc;
  font-family:Arial;
">

  <script>
    // Scroll en el documento padre (evita que abra la página dentro del resumen)
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
""").strip()

components.html(resumen_html, height=600, scrolling=True)


# ==========================
# CREA LA TABLA PARA DESCARGAR
# ==========================

st.subheader("📊 Resultados del Análisis Técnico")
st.dataframe(tabla, use_container_width=True)

st.download_button(
    label="📥 Descargar CSV",
    data=tabla.to_csv(index=False),
    file_name="resultados_trading.csv",
    mime="text/csv"
)

import streamlit.components.v1 as components

# ==========================
# TARJETAS HTML SIN RESTRICCIÓN
# ==========================
st.subheader("📊 Análisis Individual por Acción")

# for _, fila in tabla.iterrows():
#Agregue este 
for _, fila in tabla.iterrows():
    anchor_id = str(fila["Ticker"]).replace(".", "-")
    st.markdown(
        f'<div id="{anchor_id}" style="position:relative; top:-80px;"></div>',
        unsafe_allow_html=True
    )

  
    
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

        # ===== Semáforo KDJ =====
    K_val = float(fila["K"])
    D_val = float(fila["D"])

    if K_val > D_val:
        kdj_estado = "Alcista"
        kdj_color = "🟢"   # Comprar
    elif abs(K_val - D_val) < 1:
        kdj_estado = "Neutral"
        kdj_color = "🟡"   # Esperar
    else:
        kdj_estado = "Bajista"
        kdj_color = "🔴"   # Vender

    # ==========================
    # SEMÁFORO FINAL (SCORING)
    # ==========================
    score = 0
    razones = []

    # --- MACD ---
    macd_val = float(fila["MACD"])
    signal_val = float(fila["Signal"])
    if macd_val > signal_val:
        score += 1
        razones.append("MACD alcista")
    else:
        score -= 1
        razones.append("MACD bajista")

    # --- RSI ---
    rsi_val = float(fila["RSI"])
    if rsi_val < 30:
        score += 1
        razones.append("RSI sobreventa (<30)")
    elif rsi_val > 70:
        score -= 1
        razones.append("RSI sobrecompra (>70)")
    else:
        razones.append("RSI normal (30–70)")

    # --- Bollinger ---
    boll_estado = str(fila["Bollinger Señal"])
    if boll_estado == "Sobreventa":
        score += 1
        razones.append("Bollinger sobreventa")
    elif boll_estado == "Sobrecompra":
        score -= 1
        razones.append("Bollinger sobrecompra")
    else:
        razones.append("Bollinger normal")

    # --- Tendencia (EMA50 vs EMA200) ---
    tendencia = str(fila["Tendencia"])
    if tendencia == "Alcista":
        score += 1
        razones.append("Tendencia alcista (EMA50>EMA200)")
    else:
        score -= 1
        razones.append("Tendencia bajista (EMA50<EMA200)")

    # --- Precio vs EMA50 (timing) ---
    precio_ema50 = str(fila["Precio EMA50"])
    if precio_ema50 == "Arriba":
        score += 1
        razones.append("Precio arriba EMA50")
    else:
        score -= 1
        razones.append("Precio debajo EMA50")

    # --- KDJ ---
    K_val = float(fila["K"])
    D_val = float(fila["D"])
    if K_val > D_val:
        score += 1
        razones.append("KDJ alcista (K>D)")
    else:
        score -= 1
        razones.append("KDJ bajista (K<D)")

    # --- Interpretación del score ---
    if score >= 4:
        semaforo_final = "🟢 COMPRA FUERTE"
    elif score >= 2:
        semaforo_final = "🟢 POSIBLE COMPRA"
    elif score <= -4:
        semaforo_final = "🔴 VENTA FUERTE"
    elif score <= -2:
        semaforo_final = "🔴 POSIBLE VENTA"
    else:
        semaforo_final = "🟡 ESPERAR"

    # Explicación corta (top 4 razones)
    explicacion_score = " | ".join(razones[:4]) + (" | ..." if len(razones) > 4 else "")

    
    html = f"""
    <div style="
    background-color:#ffffff;
    padding:25px;
    border-radius:20px;
    margin-bottom:25px;
    border:1px solid #cccccc;
    font-family:Arial;

#    max-height: 820px;
#    overflow-y: auto;
#    -webkit-overflow-scrolling: touch;
">


        <h2 style="margin:0; font-size:26px;">
            📌 <strong>{fila['Ticker']}</strong> —
            <span style="color:#0066ff;">{fila['Señal Final']}</span>
        </h2>

        <p style="font-size:18px; margin-top:10px;">
            💲 <strong>Precio actual:</strong> {fila['Precio']}
        </p>

        <h3 style="margin-top:20px;">🚦 Semáforo Final (Score)</h3>
        <p style="font-size:17px;">
            <strong>{semaforo_final}</strong><br>
            <strong>Score:</strong> {score} / 6<br>
            <small>{explicacion_score}</small>
        </p>

        <h3 style="margin-top:20px;">🎯 Gestión de riesgo (ATR)</h3>
        <p style="font-size:17px;">
            <strong>{fila["Semáforo ATR"]}</strong><br>    
            <strong>ATR(14):</strong> {fila.get('ATR14','')} &nbsp; | &nbsp;
            <strong>ATR%:</strong> {fila.get('ATR%','')}%<br>
            <strong>Tipo de Stop:</strong> {fila.get('Tipo Stop','—')}<br>
            <strong>Stop sugerido:</strong> {fila.get('Stop Sugerido','')}<br>
            <strong>TP1:</strong> {fila.get('TP1','')} &nbsp; | &nbsp;
            <strong>TP2:</strong> {fila.get('TP2','')}<br>
            <strong>Riesgo%:</strong> {fila.get('Riesgo%','')}%
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

        <h3 style="margin-top:20px;">📊 KDJ (Momentum)</h3>
        <p style="font-size:17px;">
            {kdj_color} <strong>{kdj_estado}</strong><br>
            <strong>K:</strong> {fila['K']}<br>
            <strong>D:</strong> {fila['D']}<br>
            <strong>J:</strong> {fila['J']}<br>
            <small>
                Interpretación: 🟢 K&gt;D (impulso alcista) |
                🟡 K≈D (sin dirección) |
                🔴 K&lt;D (impulso bajista)
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

    components.html(html, height=1080)
components.html(
"""
<script>
(function () {
  const doc = window.parent.document;

  // evita duplicarlo
  if (doc.getElementById("scrollTopBtn")) return;

  const btn = doc.createElement("button");
  btn.id = "scrollTopBtn";
  btn.innerHTML = "⬆";
  btn.title = "Subir al inicio";

  btn.style.position = "fixed";
  btn.style.bottom = "190px";     // ajusta si estorba algo
  btn.style.right = "20px";
  btn.style.zIndex = "999999";
  btn.style.background = "#0066ff";
  btn.style.color = "white";
  btn.style.border = "none";
  btn.style.borderRadius = "50%";
  btn.style.width = "55px";
  btn.style.height = "55px";
  btn.style.fontSize = "26px";
  btn.style.cursor = "pointer";
  btn.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";

  function scrollToTop() {
    // Intentar varios contenedores (según versión / hosting)
    const candidates = [
      doc.querySelector('[data-testid="stMain"]'),
      doc.querySelector('[data-testid="stAppViewContainer"]'),
      doc.documentElement,
      doc.body
    ];

    for (const el of candidates) {
      if (!el) continue;
      try {
        el.scrollTo({ top: 0, behavior: "smooth" });
        return;
      } catch (e) {}
    }

    // Último recurso
    try { window.parent.scrollTo(0, 0); } catch (e) {}
  }

  btn.addEventListener("click", scrollToTop);
  doc.body.appendChild(btn);
})();
</script>
""",
height=0,
)
















