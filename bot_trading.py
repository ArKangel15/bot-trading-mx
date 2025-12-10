import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
from datetime import datetime

# ============================================================
#               FUNCIONES DE INDICADORES TÉCNICOS
# ============================================================

def macd_manual(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_series = ema12 - ema26
    macd_value = macd_series.iloc[-1]
    signal_value = macd_series.ewm(span=9, adjust=False).mean().iloc[-1]
    return float(macd_value), float(signal_value)


def bollinger_manual(close):
    mid = close.rolling(20).mean().iloc[-1]
    std = close.rolling(20).std().iloc[-1]
    upper = mid + 2 * std
    lower = mid - 2 * std
    return float(upper), float(lower)


def kdj_manual(high, low, close):
    low_min = low.rolling(14).min().iloc[-1]
    high_max = high.rolling(14).max().iloc[-1]
    rsv = ((close.iloc[-1] - low_min) / (high_max - low_min)) * 100
    K = (2/3) * 50 + (1/3) * rsv
    D = (2/3) * 50 + (1/3) * K
    J = 3 * K - 2 * D
    return float(K), float(D), float(J)

def rsi_manual(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])


# ============================================================
#                    ANALIZAR UNA ACCIÓN
# ============================================================

def analizar(ticker):
    data = yf.download(ticker, period="6mo", interval="1d")

    if data.empty:
        return None

    precio = float(data["Close"].iloc[-1])

    # Indicadores base
    macd, signal = macd_manual(data["Close"])
    upper, lower = bollinger_manual(data["Close"])
    K, D, J = kdj_manual(data["High"], data["Low"], data["Close"])
    rsi = rsi_manual(data["Close"])

    # Medias móviles
    ema20 = float(data["Close"].ewm(span=20).mean().iloc[-1])
    ema50 = float(data["Close"].ewm(span=50).mean().iloc[-1])
    ema200 = float(data["Close"].ewm(span=200).mean().iloc[-1])

    # Volumen
    vol = float(data["Volume"].iloc[-1])
    vol_avg20 = float(data["Volume"].rolling(20).mean().iloc[-1])

    explicacion = []

    # ================= Señales individuales =================

    # MACD
    macd_estado = "🟢 Alcista" if macd > signal else "🔴 Bajista"
    explicacion.append("MACD > SIGNAL → alcista" if macd > signal else "MACD < SIGNAL → bajista")

    # Bollinger
    if precio < lower:
        bol_estado = "🟢 Sobreventa"
    elif precio > upper:
        bol_estado = "🔴 Sobrecompra"
    else:
        bol_estado = "🟡 Normal"
    explicacion.append("Bollinger OK")

    # KDJ
    kdj_estado = "🟢 Alcista" if K > D else "🔴 Bajista"
    explicacion.append("K > D → impulso alcista" if K > D else "K < D → impulso bajista")

    # RSI con semáforo
    if rsi > 65:
        rsi_estado = "🔴 Alto (sobrecompra)"
    elif rsi < 45:
        rsi_estado = "🟢 Fuerte (barato)"
    else:
        rsi_estado = "🟡 Normal"

    # Tendencia EMA50 / EMA200
    if ema50 > ema200:
        tendencia_estado = "🟢 Alcista"
    elif abs(ema50 - ema200) < 1:
        tendencia_estado = "🟡 Neutral"
    else:
        tendencia_estado = "🔴 Bajista"

    # Precio vs EMA50
    precio_vs_ema50 = "🟢 Encima" if precio > ema50 else "🔴 Debajo"

    # Volumen vs promedio
    volumen_estado = "🟢 Fuerte" if vol > vol_avg20 else "🟡 Normal"

    # ================= Señal Final =================
    if macd > signal and K > D and precio < lower:
        señal = "COMPRA FUERTE"
    elif macd < signal and K < D and precio > upper:
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
        "Banda Superior": round(upper, 2),
        "Banda Inferior": round(lower, 2),
        "K": round(K, 2),
        "D": round(D, 2),
        "J": round(J, 2),
        "RSI": round(rsi, 2),
        "EMA20": round(ema20, 2),
        "EMA50": round(ema50, 2),
        "EMA200": round(ema200, 2),
        "Volumen": round(vol, 0),
        "Volumen Promedio 20": round(vol_avg20, 0),

        # Estados con semáforo
        "MACD Estado": macd_estado,
        "Bollinger Estado": bol_estado,
        "KDJ Estado": kdj_estado,
        "RSI Estado": rsi_estado,
        "Tendencia": tendencia_estado,
        "Precio EMA50": precio_vs_ema50,
        "Volumen Estado": volumen_estado,

        "Señal Final": señal,
        "Explicación": " | ".join(explicacion)
    }


# ============================================================
#                   LISTA DE ACCIONES
# ============================================================

acciones = [
    "HERDEZ.MX", "TLEVISACPO.MX", "MEGACPO.MX", "VOLARA.MX",
    "AUTLANB.MX", "RA.MX", "OMAB.MX", "GAPB.MX",
    "ALSEA.MX", "BIMBOA.MX", "GFINBURO.MX", "SORIANAB.MX",
    "AC.MX", "GFNORTEO.MX", "PINFRA.MX", "GRUMAB.MX",
    "ORBIA.MX", "KIMBERA.MX", "LABB.MX", "CHDRAUIB.MX",
    "GCARSOA1.MX", "VESTA.MX", "BBAJIOO.MX"
]

