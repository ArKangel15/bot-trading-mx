import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands


# ============================================================
#                    ANALIZAR UNA ACCIÓN
# ============================================================
def analizar(ticker):
    try:
        data = yf.download(ticker, period="6mo", interval="1d")
        if data.empty:
            return None
    except:
        return None

    close = data["Close"]

    # ================= INDICADORES =================

    # MACD
    macd_ind = MACD(close)
    data["MACD"] = macd_ind.macd()
    data["SIGNAL"] = macd_ind.macd_signal()

    # KDJ
    low = data["Low"].rolling(14).min()
    high = data["High"].rolling(14).max()
    data["RSV"] = (close - low) / (high - low) * 100
    data["K"] = data["RSV"].ewm(alpha=1/3).mean()
    data["D"] = data["K"].ewm(alpha=1/3).mean()
    data["J"] = 3 * data["K"] - 2 * data["D"]

    # RSI
    rsi = RSIIndicator(close)
    data["RSI"] = rsi.rsi()

    # EMAs
    data["EMA50"] = EMAIndicator(close, 50).ema_indicator()
    data["EMA200"] = EMAIndicator(close, 200).ema_indicator()

    # Bollinger Bands
    bb = BollingerBands(close)
    data["boll_low"] = bb.bollinger_lband()
    data["boll_high"] = bb.bollinger_hband()

    # Volumen
    data["vol_prom20"] = data["Volume"].rolling(20).mean()

    # ================= OBTENER ÚLTIMO DATO =================

    u = data.iloc[-1]

    precio = float(u["Close"])
    macd = float(u["MACD"])
    signal = float(u["SIGNAL"])
    K = float(u["K"])
    D = float(u["D"])
    RSI = float(u["RSI"])
    EMA50 = float(u["EMA50"])
    EMA200 = float(u["EMA200"])
    boll_low = float(u["boll_low"])
    boll_high = float(u["boll_high"])
    vol = float(u["Volume"])
    vol_prom = float(u["vol_prom20"])

    # ================= SEÑALES INDIVIDUALES =================

    señales = []

    # Tendencia
    if EMA50 > EMA200:
        señales.append("Tendencia Alcista (EMA50 > EMA200)")
    else:
        señales.append("Tendencia Bajista (EMA50 < EMA200)")

    # MACD
    if macd > signal:
        señales.append("MACD Alcista")
    else:
        señales.append("MACD Bajista")

    # KDJ
    if K > D:
        señales.append("KDJ Alcista (K > D)")
    else:
        señales.append("KDJ Bajista (K < D)")

    # RSI
    if 45 <= RSI <= 65:
        señales.append("RSI Saludable")
    elif RSI < 30:
        señales.append("RSI Sobrevendido")
    elif RSI > 70:
        señales.append("RSI Sobrecomprado")

    # Volumen
    if vol > vol_prom:
        señales.append("Volumen Fuerte")
    else:
        señales.append("Volumen Débil")

    # ================= SEÑAL FINAL =================

    compra_fuerte = (
        EMA50 > EMA200 and
        precio > EMA50 and
        macd > signal and
        K > D and
        45 <= RSI <= 65 and
        vol > vol_prom
    )

    venta_fuerte = (
        EMA50 < EMA200 and
        precio < EMA50 and
        macd < signal and
        K < D and
        (RSI < 30 or RSI > 70) and
        vol > vol_prom
    )

    if compra_fuerte:
        señal_final = "COMPRA FUERTE"
    elif venta_fuerte:
        señal_final = "VENTA FUERTE"
    elif macd > signal and K > D:
        señal_final = "POSIBLE COMPRA"
    elif macd < signal and K < D:
        señal_final = "POSIBLE VENTA"
    else:
        señal_final = "NEUTRO / ESPERAR"

    # ================= RETORNAR RESULTADOS =================

    return {
        "Ticker": ticker,
        "Precio": round(precio, 2),
        "MACD": round(macd, 3),
        "Signal": round(signal, 3),
        "K": round(K, 2),
        "D": round(D, 2),
        "RSI": round(RSI, 2),
        "EMA50": round(EMA50, 2),
        "EMA200": round(EMA200, 2),
        "Volumen": int(vol),
        "Vol Prom 20": int(vol_prom),
        "Bollinger Inf": round(boll_low, 2),
        "Bollinger Sup": round(boll_high, 2),
        "Señales": " | ".join(señales),
        "Señal Final": señal_final,
    }


# ============================================================
#                    LISTA DE ACCIONES (TAL COMO TENÍAS)
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


# ============================================================
#                      PROCESAR ACCIONES
# ============================================================
historial = []

for acc in acciones:
    r = analizar(acc)
    if r:
        historial.append(r)

tabla = pd.DataFrame(historial)
tabla.to_csv("historial_trading.csv", index=False)
print("\n================= TABLA DE SEÑALES =================")
print(tabla)
print("====================================================")
print("Archivo guardado: historial_trading.csv\n")

