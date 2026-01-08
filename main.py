from fastapi import FastAPI, Query
from datetime import datetime
import pytz

from bot_trading import (
    descargar_batch,
    analizar_con_data,
    acciones_mx,
    acciones_usa
)

app = FastAPI(title="Trading Arkangel API")

@app.get("/")
def root():
    return {"status": "ok", "message": "Trading Arkangel API activa"}

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

            # 👉 MISMA LÓGICA DE "OPORTUNIDAD DE COMPRA"
            if (
                r["Señal Final"] in ["COMPRA FUERTE", "POSIBLE COMPRA"]
                and r["Semáforo ATR"] == "🟢 VOLATILIDAD SANA"
                and float(r["Riesgo%"]) <= 5
            ):
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
            "setups": resultados
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
