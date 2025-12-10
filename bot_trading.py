import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
from datetime import datetime

# ============================================================
#                MACD MANUAL
# ============================================================
def macd_manual(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()

    macd_series = ema12 - ema26
    signal_series = macd_series.ewm(span=9, adjust=False).mean()

    return float(macd_series.iloc[-1]), float(signal_series.iloc[-1])


# ============================================================
#             BOLLINGER BANDS MANUAL
# ============================================================
def bollinger_manual(close):
    mid = close.rolling(20).mean().iloc[-1]
    std = close.rolling(20).std().iloc[-1]

    upper = mid + 2 * std
    lower = mid - 2 * std

    return float(upper), float(lower)


# ============================================================
#                     KDJ MANUAL
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
#                    ANALIZADOR PRINCIPAL
# ============================================================
def analizar(ticker):

    data = yf.download(ticker, period="6mo", interval="1d")

    if data.empty:
        return None

    close = data["Close"]
    high = data["High"]
    low = data["Low"]

    precio = float(close.iloc[-1])

    # Indicadores
    macd, signal = macd_manual(close)
    upper, lower = bollinger_manual(close)
    K, D, J = kdj_manual(high, low, close)

    # ESTADOS
    macd_estado = "Alcista" if macd > signal else "Bajista"
    kdj_estado = "Alcista" if K > D else "Bajista"

    if precio < lower:
        bollinger_estado = "Sobreventa"
    elif precio > upper:
        bollinger_estado = "Sobrecompra"
    else:
        bollinger_estado = "Normal"

    # Señal final simplificada y estable
    if macd > signal and precio < lower and K > D:
        señal = "COMPRA FUERTE"
    elif macd < signal and precio > upper and K < D:
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

        "MACD": round(macd, 4),
        "Signal": round(signal, 4),
        "MACD Señal": macd_estado,

        "Banda Superior": round(upper, 2),
        "Banda Inferior": round(lower, 2),
        "Bollinger Señal": bollinger_estado,

        "K": round(K, 2),
        "D": round(D, 2),
        "J": round(J, 2),
        "KDJ Señal": kdj_estado,

        "Señal Final": señal,
        "Explicación": f"MACD: {macd_estado} | Bollinger: {bollinger_estado} | KDJ: {kdj_estado}"
    }


# ============================================================
#                  LISTA DE ACCIONES MX
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
    "BBAJIOO.MX"
]


