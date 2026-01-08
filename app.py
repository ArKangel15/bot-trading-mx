from fastapi import FastAPI, Query
from datetime import datetime
import pytz
import pandas as pd

from bot_trading import (
    descargar_batch,
    analizar_con_data,
    acciones_mx,
    acciones_usa,
)

app = FastAPI(title="Trading Arkangel API")

# =========================================================
# UTILIDADES
# =========================================================
def to_float(x):
    try:
        if x is None or x == "":
            return None
        return float(x)
    except:
        return None


def es_setup_perfecto(row: dict) -> bool:
    """
    MISMA lógica que Streamlit - Oportunidad de compra
    """

    sem = str(row.get("Semáforo Final", "")).upper()
    atr_sem = str(row.get("Semáforo ATR", "")).upper()

    score = to_float(row.get("Score"))
    riesgo = to_float(row.get("Riesgo%"))
    precio = to_float(row.get("Precio"))
    soporte = to_float(row.get("Soporte Estadístico"))
    medio = to_float(row.get("Precio Medio"))
    cara = to_float(row.get("Zona Cara"))

    # 1️⃣ Señal
    if "COMPRA FUERTE" not in sem and "POSIBLE COMPRA" not in sem:
        return False

    # 2️⃣ Volatilidad sana
    if "SANA" not in atr_sem:
        return False

    # 3️⃣ Score mínimo
    if score is None or score < 3:
        return False

    # 4️⃣ Riesgo máximo
    if riesgo is None or riesgo > 5:
        return False

    # 5️⃣ Zona de precio
    if precio is None or soporte is None or medio is None or cara is None:
        return False

    if precio > medio:
        return False

    if precio >= cara:
        return False

    return True


# =========================================================
# ENDPOINTS
# =========================================================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Trading Arkangel API activa"
    }


@app.get("/oportunidad-compra")
def oportunidad_compra(market: str = Query("MX")):
    """
    Devuelve SOLO setups perfectos.
    Si no hay ninguno -> total = 0 y setups = []
    """

    try:
        acciones = acciones_mx if market.upper() == "MX" else acciones_usa

        batch = descargar_batch(acciones, period="2y", interval="1d")

        tz_mx = pytz.timezone("America/Mazatlan")
        timestamp = datetime.now(tz_mx).strftime("%Y-%m-%d %H:%M:%S")

        resultados = []

        for ticker in acciones:

            # Validar que venga en batch
            if not isinstance(batch.columns, pd.MultiIndex):
                continue

            if ticker not in batch.columns.get_level_values(0):
                continue

            df = batch[ticker].dropna()
            r = analizar_con_data(ticker, df)

            if not r:
                continue

            # 👉 FILTRO REAL DE SETUP PERFECTO
            if not es_setup_perfecto(r):
                continue

            resultados.append({
                "ticker": r["Ticker"],
                "senal": r["Semáforo Final"],
                "precio": r["Precio"],
                "soporte": r["Soporte Estadístico"],
                "precio_medio": r["Precio Medio"],
                "zona_cara": r["Zona Cara"],
                "score": r["Score"],
                "riesgo_pct": r["Riesgo%"],
                "atr_pct": r["ATR%"],
                "stop": r["Stop Sugerido"],
                "tp1": r["TP1"],
                "tp2": r["TP2"],
                "timestamp": timestamp
            })

        return {
            "status": "ok",
            "market": market.upper(),
            "hay_oportunidad": len(resultados) > 0,
            "total": len(resultados),
            "setups": resultados
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
