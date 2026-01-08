from fastapi import FastAPI, Query
from datetime import datetime
import pytz
import pandas as pd

from bot_trading import (
    descargar_batch,
    analizar_con_data,
    acciones_mx,
    acciones_usa
)

app = FastAPI(title="Trading Arkangel API")

# ======================================================
# ROOT
# ======================================================
@app.get("/")
def root():
    return {"status": "ok", "message": "Trading Arkangel API activa"}

# ======================================================
# SEMÁFORO ATR (MISMO QUE STREAMLIT)
# ======================================================
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

# ======================================================
# SETUP PERFECTO (MISMA LÓGICA STREAMLIT)
# ======================================================
def es_setup_perfecto(r):
    try:
        sem = str(r["Señal Final"]).upper()
        atr_sem = semaforo_atr(r["ATR%"])
        score = float(r.get("Score", 0))
        riesgo = float(r["Riesgo%"])
        precio = float(r["Precio"])
        soporte = float(r["Soporte Estadístico"])
        medio = float(r["Precio Medio"])
        cara = float(r["Zona Cara"])
    except:
        return False

    # 1) Señal
    if "COMPRA FUERTE" not in sem and "POSIBLE COMPRA" not in sem:
        return False

    # 2) Volatilidad sana
    if atr_sem != "🟢 VOLATILIDAD SANA":
        return False

    # 3) Score mínimo
    if score < 3:
        return False

    # 4) Riesgo máximo
    if riesgo > 5:
        return False

    # 5) Precio en zona barata (P20–P50) y NO zona cara
    if precio > medio:
        return False
    if precio >= cara:
        return False

    return True

# ======================================================
# ENDPOINT OPORTUNIDAD DE COMPRA
# ======================================================
@app.get("/oportunidad-compra")
def oportunidad_compra(market: str = Query("MX")):
    try:
        acciones = acciones_mx if market.upper() == "MX" else acciones_usa
        batch = descargar_batch(acciones, period="2y", interval="1d")

        resultados = []
        tz_mx = pytz.timezone("America/Mazatlan")
        timestamp = datetime.now(tz_mx).strftime("%Y-%m-%d %H:%M:%S")

        for ticker in acciones:
            if ticker not in batch.columns.get_level_values(0):
                continue

            df = batch[ticker].dropna()
            r = analizar_con_data(ticker, df)
            if not r:
                continue

            # 👉 SOLO SETUP PERFECTO
            if es_setup_perfecto(r):
                resultados.append({
                    "ticker": r["Ticker"],
                    "senal": r["Señal Final"],
                    "precio": r["Precio"],
                    "stop": r["Stop Sugerido"],
                    "tp1": r["TP1"],
                    "tp2": r["TP2"],
                    "riesgo_pct": r["Riesgo%"],
                    "atr_pct": r["ATR%"],
                    "timestamp": timestamp
                })

        return {
            "status": "ok",
            "market": market.upper(),
            "hay_oportunidad": len(resultados) > 0,
            "total": len(resultados),
            "timestamp": timestamp,
            "setups": resultados
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
