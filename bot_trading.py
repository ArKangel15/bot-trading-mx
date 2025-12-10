import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
from datetime import datetime

# ============================================================
#                    MACD MANUAL
# ============================================================
def macd_manual(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    macd_series = ema12 - ema26
    signal_series = macd_series.ewm(span=9, adjust=False).mean()

    return float(macd_series.iloc[-1]), float(signal_series.iloc[-1])


# ============================================================
#               BOLLINGER BANDS MANUAL
# ============================================================
def bollinger_manual(close):
    mid = close.rolling(20).mean().iloc[-1]
    std = close.rolling(20).std().iloc[-1]

    upper = mid + (2 * std)
    lower = mid - (2 * std)

    return float(upper), float(lower)


# ============================================================
#                       KDJ MANUAL
# ============================================================
def kdj_manual(high, low, close):
    low_min = low.rolling(14).min().iloc[-1]
    high_max = high.rolling(14).max().iloc[-1]

    rsv = ((close.iloc[-1] - low_min) / (high_max - low_min)) * 100

    K = (2/3) * 50 + (1/3) * rsv
    D = (2/3) * 50 + (1/3) * K
    J = 3 * K - 2 * D

    return float(K), float(D), float(J)


# ============================================================
#                   RSI (14)
# ============================================================
def rsi_manual(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()

    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))

    return float(RSI.iloc[-1])


# ============================================================
#         TENDENCIAS CON EMA20 – EMA50 – EMA200
# ============================================================
def calcular_emas(close):
    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
    ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
    ema200 = float(close.ewm(span=200, adjust=False).mean().iloc[-1])
    return ema20, ema50, ema200


# ============================================================
#                     VOLÚMENES
# ============================================================
def volumen_indicadores(data):
    vol_actual = float(data["Volume"].iloc[-1])
    vol_prom20 = float(data["Volume"].rolling(20).mean().iloc[-1])

    if vol_actual > vol_prom20 * 1.5:
        estado = "Alto (fuerte interés)"
    elif vol_actual < vol_prom20 * 0.6:
        estado = "Bajo (desinterés)"
    else:
        estado = "Normal"

    return vol_actual, vol_prom20, estado


# ============================================================
#                  ANALIZAR UNA ACCIÓN
# ============================================================
def analizar(ticker):

    data = yf.download(ticker, period="6mo", interval="1d")

    if data.empty:
        return None

    precio = float(data["Close"].iloc[-1])

    # Indicadores originales
    macd, signal = macd_manual(data["Close"])
    upper, lower = bollinger_manual(data["Close"])
    K, D, J = kdj_manual(data["High"], data["Low"], data["Close"])

    # Indicadores nuevos
    rsi = rsi_manual(data["Close"])
    ema20, ema50, ema200 = calcular_emas(data["Close"])
    vol_actual, vol_prom20, vol_estado = volumen_indicadores(data)

    # Señales descriptivas
    macd_estado = "Alcista" if macd > signal else "Bajista"
    kdj_estado = "Alcista" if K > D else "Bajista"

    if precio < lower:
        bollinger_estado = "Sobreventa"
    elif precio > upper:
        bollinger_estado = "Sobrecompra"
    else:
        bollinger_estado = "Normal"

    # Tendencia general
    if ema50 > ema200:
        tendencia = "Alcista"
    elif ema50 < ema200:
        tendencia = "Bajista"
    else:
        tendencia = "Neutral"

    # Señal final mejorada (estilo Bloomberg)
    if macd > signal and rsi < 35 and precio < lower and tendencia == "Alcista":
        señal = "COMPRA FUERTE"
    elif macd < signal and rsi > 70 and precio > upper and tendencia == "Bajista":
        señal = "VENTA FUERTE"
    elif macd > signal or K > D:
        señal = "POSIBLE COMPRA"
    elif macd < signal or K < D:
        señal = "POSIBLE VENTA"
    else:
        señal = "ESPERAR"

    return {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Ticker": ticker,
        "Precio": round(precio, 2),

        # Indicadores clásicos
        "MACD": round(macd, 4),
        "Signal": round(signal, 4),
        "MACD Señal": macd_estado,
        "Bollinger Señal": bollinger_estado,
        "KDJ Señal": kdj_estado,

        # Rangos
        "Banda Superior": round(upper, 2),
        "Banda Inferior": round(lower, 2),

        # Nuevos indicadores
        "RSI": round(rsi, 2),
        "EMA20": round(ema20, 2),
        "EMA50": round(ema50, 2),
        "EMA200": round(ema200, 2),

        "Volumen": round(vol_actual, 2),
        "Volumen Promedio 20": round(vol_prom20, 2),
        "Volumen Estado": vol_estado,

        "Tendencia": tendencia,

        "Señal Final": señal,
        "Explicación": (
            f"MACD {macd_estado} | "
            f"KDJ {kdj_estado} | "
            f"Bollinger {bollinger_estado} | "
            f"RSI={round(rsi,2)} | "
            f"Tendencia general: {tendencia} | "
            f"Volumen: {vol_estado}"
        )
    }


# ============================================================
#                  LISTA DE ACCIONES
# ============================================================
acciones = [
    "HERDEZ.MX",
    "TLEVISACPO.MX",
    "MEGACPO.MX",
    "VOLARA.MX",
    "AUTLANB.MX",
    "RA.MX",
    "OMAB.MX",
    "GAPB.MX",
    "ALSEA.MX",
    "BIMBOA.MX",
    "GFINBURO.MX",
    "SORIANAB.MX",
    "AC.MX",
    "GFNORTEO.MX",
    "PINFRA.MX",
    "GRUMAB.MX",
    "ORBIA.MX",
    "KIMBERA.MX",
    "LABB.MX",
    "CHDRAUIB.MX",
    "GCARSOA1.MX",
    "VESTA.MX",
    "BBAJIOO.MX",
]
