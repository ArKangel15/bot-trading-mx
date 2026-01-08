from fastapi import FastAPI
from datetime import datetime
import pytz

from bot_trading import (
    descargar_batch,
    analizar_con_data,
    acciones_mx,
    acciones_usa,
)

app = FastAPI(title="Trading Arkangel API")

tz_mx = pytz.timezone("America/Mazatlan")


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Trading Arkangel API"
    }


@app.get("/setup-perfecto")
def setup_perfecto(mercado: str = "MX"):
    """
    Devuelve SOLO setups perfectos.
    Si no hay, devuelve status=no_setup
    """

    acciones = acciones_mx if mercado.upper() == "MX" else acciones_usa

    batch = descargar_batch(acciones, period="2y", interval="1d")

    setups = []

    for ticker in acciones:
        try:
            if ticker not in batch.columns.get_level_values(0):
                continue

            df = batch[ticker].copy()
            r = analizar_con_data(ticker, df)
            if not r:
                continue

            # ==========================
            # 🔥 LÓGICA SETUP PERFECTO
            # ==========================
            sem = str(r.get("Señal Final", "")).upper()
            atr_pct = r.get("ATR%", None)
            score = r.get("Score", None)
            riesgo = r.get("Riesgo%", None)

            precio = r.get("Precio")
            soporte = r.get("Soporte Estadístico")
            medio = r.get("Precio Medio")
            cara = r.get("Zona Cara")

            if "COMPRA" not in sem:
                continue
            if atr_pct is None or atr_pct > 3:
                continue
            if riesgo is None or riesgo > 5:
                continue
            if precio is None or soporte == "" or medio == "" or cara == "":
                continue
            if precio > medio or precio >= cara:
                continue

            setups.append({
                "ticker": ticker,
                "senal": sem,
                "precio": precio,
                "stop": r.get("Stop Sugerido"),
                "tp1": r.get("TP1"),
                "tp2": r.get("TP2"),
                "riesgo_pct": riesgo,
                "atr_pct": atr_pct,
                "timestamp": datetime.now(tz_mx).isoformat()
            })

        except Exception:
            continue

    if not setups:
        return {
            "status": "no_setup",
            "timestamp": datetime.now(tz_mx).isoformat()
        }

    return {
        "status": "ok",
        "total": len(setups),
        "setups": setups
    }
