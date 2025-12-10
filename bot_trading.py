import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
from datetime import datetime

# ============================================================
#                  MACD MANUAL
# ============================================================
def macd_manual(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    
    macd_value = ema12.iloc[-1] - ema26.iloc[-1]

    macd_series = ema12 - ema26
    signal_value = macd_series.ewm(span=9, adjust=False).mean().iloc[-1]

    return macd_value, signal_value


# ============================================================
#               BOLLINGER BANDS MANUAL
# ============================================================
def bollinger_manual(close):
    mid = close.rolling(20).mean().iloc[-1]
    std = close.rolling(20).std().iloc[-1]

    upper = mid + (std * 2)
    lower = mid - (std * 2)

    return upper, lower


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

    return K, D, J

# ============================================================
#                    ANALIZAR UNA ACCIÓN
# ============================================================
def analizar(ticker):

    data = yf.download(ticker, period="6mo", interval="1d")

    if data.empty:
        return None

    precio = float(data["Close"].iloc[-1])

    # Indicadores manuales
    macd, signal = macd_manual(data["Close"])
    upper, lower = bollinger_manual(data["Close"])
    K, D, J = kdj_manual(data["High"], data["Low"], data["Close"])

    # Convertir a float (importantísimo para evitar Series)
    macd = float(macd)
    signal = float(signal)
    upper = float(upper)
    lower = float(lower)
    K = float(K)
    D = float(D)
    J = float(J)

    explicacion = []

    # ===== Señales independientes =====

    # MACD
    if macd > signal:
        macd_sig = "MACD Alcista"
        explicacion.append("MACD > SIGNAL → tendencia alcista")
    else:
        macd_sig = "MACD Bajista"
        explicacion.append("MACD < SIGNAL → tendencia bajista")

    # Bollinger
    if precio < lower:
        bol_sig = "Sobreventa (Bollinger)"
        explicacion.append("Precio bajo banda inferior → sobreventa")
    elif precio > upper:
        bol_sig = "Sobrecompra (Bollinger)"
        explicacion.append("Precio sobre banda superior → sobrecompra")
    else:
        bol_sig = "Normal"
        explicacion.append("Precio dentro de canal normal")

    # KDJ
    if K > D:
        kdj_sig = "KDJ Alcista"
        explicacion.append("K > D → impulso alcista")
    else:
        kdj_sig = "KDJ Bajista"
        explicacion.append("K < D → impulso bajista")

    # ===== Señal final combinada =====
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
        "Banda Superior": round(upper, 2),
        "Banda Inferior": round(lower, 2),
        "K": round(K, 2),
        "D": round(D, 2),
        "J": round(J, 2),
        "MACD Señal": macd_sig,
        "Bollinger Señal": bol_sig,
        "KDJ Señal": kdj_sig,
        "Señal Final": señal,
        "Explicación": " | ".join(explicacion)
    }

# ============================================================
#                       ACCIONES A ANALIZAR
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


historial = []

for acc in acciones:
    r = analizar(acc)
    if r:
        historial.append(r)

# Convertir a tabla
tabla = pd.DataFrame(historial)

print("\n\n================ TABLA DE SEÑALES =================\n")
print(tabla)
print("\n===================================================\n")

# Guardar historial
tabla.to_csv("historial_trading.csv", index=False)
print("💾 Archivo guardado: historial_trading.csv\n")


