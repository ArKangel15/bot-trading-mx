from fastapi import FastAPI, Query
from datetime import datetime
import pytz
import pandas as pd

from bot_trading import descargar_batch, analizar_con_data, acciones_mx, acciones_usa

app = FastAPI(title="Trading Arkangel API", version="1.0.0")

# -----------------------------
# Helpers (igual que Streamlit)
# -----------------------------
def to_float(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except:
        return None

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

def calcular_score_y_semaforo(row: dict):
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

def es_setup_perfecto(row: dict):
    """
    MISMA lógica que tu Streamlit:
    - compra fuerte o posible compra
    - ATR sano
    - Score >= 3
    - Riesgo <= 5%
    - Precio <= P50 y < P80 (zona cara)
    """
    sem = str(row.get("Semáforo Final", "")).upper()
    atr_sem = str(row.get("Semáforo ATR", "")).upper()
    score = to_float(row.get("Score", None))
    riesgo = to_float(row.get("Riesgo%", None))
    precio = to_float(row.get("Precio", None))
    soporte = to_float(row.get("Soporte Estadístico", None))
    medio = to_float(row.get("Precio Medio", None))
    cara = to_float(row.get("Zona Cara", None))

    # 1) Señal (momentum)
    if "COMPRA FUERTE" not in sem and "POSIBLE COMPRA" not in sem:
        return False

    # 2) Volatilidad operable
    if "SANA" not in atr_sem:
        return False

    # 3) Score mínimo
    if score is None or score < 3:
        return False

    # 4) Riesgo máximo
    if riesgo is None or riesgo > 5:
        return False

    # 5) Precio en zona “barata”
    if precio is None or soporte is None or medio is None or cara is None:
        return False

    if precio > medio:
        return False
    if precio >= cara:
        return False

    return True


# -----------------------------
# Endpoint principal
# -----------------------------
@app.get("/oportunidad-compra")
def oportunidad_compra(
    market: str = Query("MX", pattern="^(MX|USA)$"),
    period: str = Query("2y"),
    interval: str = Query("1d"),
):
    """
    Devuelve SOLO setups perfectos (la sección 'Oportunidad de compra' de tu Streamlit)
    - si no hay: hay_oportunidad=false y setups=[]
    """

    tz = pytz.timezone("America/Mazatlan")
    batch_ts = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    tickers = acciones_mx if market == "MX" else acciones_usa
    batch = descargar_batch(tickers, period=period, interval=interval)

    resultados = []
    for t in tickers:
        try:
            if isinstance(batch.columns, pd.MultiIndex):
                if t not in batch.columns.get_level_values(0):
                    continue
                df_t = batch[t].copy()
            else:
                df_t = batch.copy()

            r = analizar_con_data(t, df_t)
            if r:
                resultados.append(r)
        except:
            continue

    if not resultados:
        return {
            "status": "ok",
            "market": market,
            "hay_oportunidad": False,
            "total": 0,
            "timestamp": batch_ts,
            "setups": []
        }

    # Enriquecer: Score + Semáforo Final + Semáforo ATR (igual que Streamlit)
    for r in resultados:
        score, sem_final = calcular_score_y_semaforo(r)
        r["Score"] = score
        r["Semáforo Final"] = sem_final
        r["Semáforo ATR"] = semaforo_atr(r.get("ATR%"))

    # Filtrar SETUPS PERFECTOS
    setups = []
    for r in resultados:
        if es_setup_perfecto(r):
            setups.append({
                "ticker": r.get("Ticker"),
                "senal": r.get("Semáforo Final"),
                "precio": r.get("Precio"),
                "stop": r.get("Stop Sugerido"),
                "tp1": r.get("TP1"),
                "tp2": r.get("TP2"),
                "riesgo_pct": r.get("Riesgo%"),
                "atr_pct": r.get("ATR%"),
                "timestamp": r.get("Fecha"),
            })

    return {
        "status": "ok",
        "market": market,
        "hay_oportunidad": len(setups) > 0,
        "total": len(setups),
        "timestamp": batch_ts,
        "setups": setups
    }


# (Opcional) Root para evitar 405 al entrar al dominio
@app.get("/")
def root():
    return {"status": "ok", "message": "Trading Arkangel API running"}
