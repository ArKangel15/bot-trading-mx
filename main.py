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


# =========================
# Helpers (igual que Streamlit)
# =========================
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


def calcular_score_y_semaforo(r: dict):
    """
    Copia directa de tu calcular_score_y_semaforo(row) en Streamlit
    pero leyendo desde el dict 'r' que regresa analizar_con_data.
    """
    score = 0

    # MACD
    macd_val = float(r.get("MACD", 0))
    signal_val = float(r.get("Signal", 0))
    score += 1 if macd_val > signal_val else -1

    # RSI
    rsi_val = float(r.get("RSI", 50))
    if rsi_val < 30:
        score += 1
    elif rsi_val > 70:
        score -= 1

    # Bollinger
    boll = str(r.get("Bollinger Señal", ""))
    if boll == "Sobreventa":
        score += 1
    elif boll == "Sobrecompra":
        score -= 1

    # Tendencia (EMA50 vs EMA200)
    tendencia = str(r.get("Tendencia", ""))
    score += 1 if tendencia == "Alcista" else -1

    # Precio vs EMA50
    precio_ema50 = str(r.get("Precio EMA50", ""))
    score += 1 if precio_ema50 == "Arriba" else -1

    # KDJ
    K_val = float(r.get("K", 0))
    D_val = float(r.get("D", 0))
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


def es_setup_perfecto(r: dict) -> bool:
    """
    Copia directa de tu es_setup_perfecto(row) en Streamlit,
    pero leyendo desde el dict enriquecido 'r'.
    """
    sem = str(r.get("Semáforo Final", "")).upper()
    atr_sem = str(r.get("Semáforo ATR", "")).upper()

    score = to_float(r.get("Score"))
    riesgo = to_float(r.get("Riesgo%"))
    precio = to_float(r.get("Precio"))
    soporte = to_float(r.get("Soporte Estadístico"))
    medio = to_float(r.get("Precio Medio"))
    cara = to_float(r.get("Zona Cara"))

    # 1) Señal (momentum)
    if "COMPRA FUERTE" not in sem and "POSIBLE COMPRA" not in sem:
        return False

    # 2) Volatilidad operable
    if "SANA" not in atr_sem:
        return False

    # 3) Score mínimo
    if score is None or score < 3:
        return False

    # 4) Riesgo máximo (ATR %)
    if riesgo is None or riesgo > 5:
        return False

    # 5) Precio en zona “barata” (P20 a P50) y NO en zona cara
    if precio is None or soporte is None or medio is None or cara is None:
        return False

    if precio > medio:
        return False
    if precio >= cara:
        return False

    return True


# =========================
# Endpoints
# =========================
@app.get("/")
def root():
    return {"status": "ok", "message": "Trading Arkangel API activa"}


@app.get("/oportunidad-compra")
def oportunidad_compra(market: str = Query("MX")):
    """
    Devuelve SOLO setups perfectos (igual que Streamlit).
    Si no hay -> total=0 y setups=[]
    """
    try:
        acciones = acciones_mx if market.upper() == "MX" else acciones_usa

        batch = descargar_batch(acciones, period="2y", interval="1d")

        tz = pytz.timezone("America/Mazatlan")
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        setups = []

        # Validación del batch (MultiIndex)
        if not isinstance(batch.columns, pd.MultiIndex):
            return {
                "status": "ok",
                "market": market.upper(),
                "hay_oportunidad": False,
                "total": 0,
                "setups": [],
                "warning": "Batch no vino con MultiIndex (respuesta inesperada de yfinance)."
            }

        for ticker in acciones:
            if ticker not in batch.columns.get_level_values(0):
                continue

            df = batch[ticker].dropna()
            r = analizar_con_data(ticker, df)
            if not r:
                continue

            # 1) Calcula Score + Semáforo Final (igual Streamlit)
            score, sem_final = calcular_score_y_semaforo(r)
            r["Score"] = score
            r["Semáforo Final"] = sem_final

            # 2) Calcula Semáforo ATR (igual Streamlit)
            r["Semáforo ATR"] = semaforo_atr(r.get("ATR%"))

            # 3) Filtro exacto de Setup Perfecto (igual Streamlit)
            if not es_setup_perfecto(r):
                continue

            # 4) Respuesta para n8n/Telegram
            setups.append({
                "ticker": r.get("Ticker"),
                "tipo_senal": r.get("Semáforo Final"),
                "precio_entrada": r.get("Precio"),
                "stop_loss": r.get("Stop Sugerido"),
                "tp1": r.get("TP1"),
                "tp2": r.get("TP2"),
                "riesgo_pct": r.get("Riesgo%"),
                "atr_pct": r.get("ATR%"),
                "score": r.get("Score"),
                "soporte": r.get("Soporte Estadístico"),
                "precio_medio": r.get("Precio Medio"),
                "zona_cara": r.get("Zona Cara"),
                "timestamp": timestamp,
            })

        return {
            "status": "ok",
            "market": market.upper(),
            "hay_oportunidad": len(setups) > 0,
            "total": len(setups),
            "setups": setups
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/accion")
def consultar_accion(
    ticker: str = Query(..., description="Ticker a consultar"),
    market: str = Query("MX", description="MX o USA")
):
    try:
        ticker = ticker.upper().strip()

        acciones = acciones_mx if market.upper() == "MX" else acciones_usa

        # Normalizar ticker MX
        if market.upper() == "MX" and not ticker.endswith(".MX"):
            ticker = f"{ticker}.MX"

        if ticker not in acciones:
            return {
                "status": "ok",
                "found": False,
                "message": f"{ticker} no está en la lista del mercado {market.upper()}"
            }

        batch = descargar_batch([ticker], period="2y", interval="1d")

        if not isinstance(batch.columns, pd.MultiIndex):
            return {
                "status": "error",
                "message": "Respuesta inválida de yfinance"
            }

        if ticker not in batch.columns.get_level_values(0):
            return {
                "status": "ok",
                "found": False,
                "message": "No hay datos para el ticker"
            }

        df = batch[ticker].dropna()
        r = analizar_con_data(ticker, df)
        if not r:
            return {
                "status": "ok",
                "found": False,
                "message": "No se pudo analizar la acción"
            }

        # Score + Semáforo
        score, sem_final = calcular_score_y_semaforo(r)
        r["Score"] = score
        r["Semáforo Final"] = sem_final

        # Semáforo ATR
        r["Semáforo ATR"] = semaforo_atr(r.get("ATR%"))

        tz = pytz.timezone("America/Mazatlan")
        r["timestamp"] = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "status": "ok",
            "found": True,
            "accion": {
                "ticker": r.get("Ticker"),
                "precio": r.get("Precio"),
                "semaforo": r.get("Semáforo Final"),
                "score": r.get("Score"),
                "atr_pct": r.get("ATR%"),
                "semaforo_atr": r.get("Semáforo ATR"),
                "soporte": r.get("Soporte Estadístico"),
                "precio_medio": r.get("Precio Medio"),
                "zona_cara": r.get("Zona Cara"),
                "stop": r.get("Stop Sugerido"),
                "tp1": r.get("TP1"),
                "tp2": r.get("TP2"),
                "riesgo_pct": r.get("Riesgo%"),
                "timestamp": r.get("timestamp"),
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/buscar")
def buscar_accion(
    q: str = Query(..., min_length=1),
    market: str = Query("MX")
):
    """
    Busca una acción por texto libre.
    - Si existe exacta → found = true
    - Si no existe → found = false + suggestions[]
    """

    q = q.strip().upper()

    acciones = acciones_mx if market.upper() == "MX" else acciones_usa

    # 1️⃣ Coincidencia exacta
    if q in acciones:
        return {
            "status": "ok",
            "found": True,
            "ticker": q
        }

    # 2️⃣ Coincidencias parciales (autocomplete)
    starts_with = [a for a in acciones if a.startswith(q)]
    contains = [a for a in acciones if q in a and a not in starts_with]

    # Prioridad: empieza con > contiene
    sugerencias = (starts_with + contains)[:8]

    return {
        "status": "ok",
        "found": False,
        "query": q,
        "suggestions": sugerencias,
        "message": f"{q} no está en la lista del mercado {market.upper()}"
    }
