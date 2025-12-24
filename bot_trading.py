import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd
from datetime import datetime

# ============================================================
#              DESCARGA BATCH (TODOS LOS TICKERS)
# ============================================================
def descargar_batch(tickers, period="2y", interval="1d"):
    """
    Descarga en una sola llamada los datos de todos los tickers.
    Regresa un DataFrame con columnas MultiIndex:
      nivel 0 = Ticker
      nivel 1 = Open/High/Low/Close/Adj Close/Volume
    """
    if not tickers:
        return pd.DataFrame()

    data = yf.download(
        tickers=" ".join(tickers),
        period=period,
        interval=interval,
        group_by="ticker",
        threads=True,
        auto_adjust=False
    )

    return data
    
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

    upper = mid + 2 * std
    lower = mid - 2 * std

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
#                       RSI (14)
# ============================================================
def rsi_manual(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()

    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))

    return float(RSI.iloc[-1])


# ============================================================
#                       EMAs
# ============================================================
def calcular_emas(close):
    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
    ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
    ema200 = float(close.ewm(span=200, adjust=False).mean().iloc[-1])
    return ema20, ema50, ema200

# ============================================================
#                       ATR (14)
# ============================================================
def atr_manual(high, low, close, period=14):
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()  # simple (rápido). Si quieres Wilder luego lo cambiamos.
    return float(atr.iloc[-1])

# ============================================================
#        ANALIZAR UNA ACCIÓN (USANDO DATA YA DESCARGADA)
# ============================================================
def analizar_con_data(ticker, data):

    if data is None or data.empty:
        return None

    data = data.dropna()
    if data.empty:
        return None

    close = data["Close"]
    high = data["High"]
    low = data["Low"]

    # Normalizar a Series (por si yfinance devuelve DataFrame)
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    if isinstance(high, pd.DataFrame):
        high = high.iloc[:, 0]
    if isinstance(low, pd.DataFrame):
        low = low.iloc[:, 0]

    if close.dropna().empty:
        return None

    precio = float(close.dropna().iloc[-1])

    # -------- INDICADORES --------
    macd, signal = macd_manual(close)
    upper, lower = bollinger_manual(close)
    K, D, J = kdj_manual(high, low, close)
    rsi = rsi_manual(close)
    ema20, ema50, ema200 = calcular_emas(close)

    atr14 = atr_manual(high, low, close, period=14)
    if pd.isna(atr14) or atr14 <= 0:
        return None
    atr_pct = (atr14 / precio) * 100 if precio else 0

    # -------- ESTADOS --------
    macd_estado = "Alcista" if macd > signal else "Bajista"
    kdj_estado = "Alcista" if K > D else "Bajista"

    if precio < lower:
        bollinger_estado = "Sobreventa"
    elif precio > upper:
        bollinger_estado = "Sobrecompra"
    else:
        bollinger_estado = "Normal"

    if rsi < 30:
        rsi_estado = "Sobreventa"
    elif rsi > 70:
        rsi_estado = "Sobrecompra"
    else:
        rsi_estado = "Normal"

    tendencia = "Alcista" if ema50 > ema200 else "Bajista"
    precio_ema50 = "Arriba" if precio > ema50 else "Debajo"

    # -------- SEÑAL FINAL --------
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

    # Stop/TP sugeridos SOLO para compras
    if señal in ["COMPRA FUERTE", "POSIBLE COMPRA"]:
        mult = 2.0 if señal == "COMPRA FUERTE" else 1.5
        tipo_stop = "Conservador (2 ATR)" if mult == 2.0 else "Agresivo (1.5 ATR)"
        stop_sugerido = precio - (mult * atr14)
        riesgo = precio - stop_sugerido
        tp1 = precio + (1.0 * riesgo)
        tp2 = precio + (2.0 * riesgo)
        riesgo_pct = (riesgo / precio) * 100 if precio else 0
    else:
        tipo_stop = "—"
        stop_sugerido = None
        tp1 = None
        tp2 = None
        riesgo_pct = None

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

        "RSI": round(rsi, 2),
        "RSI Estado": rsi_estado,

        "EMA20": round(ema20, 2),
        "EMA50": round(ema50, 2),
        "EMA200": round(ema200, 2),

        "Tendencia": tendencia,
        "Precio EMA50": precio_ema50,

        "Señal Final": señal,

        "ATR14": round(float(atr14), 4),
        "ATR%": round(float(atr_pct), 2),
        "Tipo Stop": tipo_stop,
        "Stop Sugerido": (round(stop_sugerido, 2) if stop_sugerido is not None else ""),
        "TP1": (round(tp1, 2) if tp1 is not None else ""),
        "TP2": (round(tp2, 2) if tp2 is not None else ""),
        "Riesgo%": (round(riesgo_pct, 2) if riesgo_pct is not None else ""),

        "Explicación": (
            f"MACD: {macd_estado} | "
            f"KDJ: {kdj_estado} | "
            f"Bollinger: {bollinger_estado} | "
            f"RSI: {rsi_estado} | "
            f"Tendencia (EMA50/EMA200): {tendencia} | "
            f"Precio vs EMA50: {precio_ema50}"
        )
    }



# ============================================================
#               LISTA DE ACCIONES DEL MERCADO MX
# ============================================================
acciones_mx = [
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
    "ALPEKA.MX",
    "AGUILASCPO.MX",
    "GMEXICOB.MX",
    "NEMAKA.MX",
    "AXTELCPO.MX",
    "CEMEXCPO.MX",
    "GENTERA.MX",
    "WALMEX.MX",
    "FEMSAUBD.MX",
    "PEP.MX",
    "COST.MX",
    "MELIN.MX",
    "AMZN.MX",
    "PE&OLES.MX",
    "FMTY14.MX",
    "FIBRAMQ12.MX",
    "GCC.MX",
    "NKE.MX",
    "ADSN.MX",
    "MAT.MX",
    "ASURB.MX",
    "AZTECACPO.MX",
    "FUNO11.MX",
    "NEXT25.MX",
    "AMXB.MX",
    "AXTELCPO.MX",
    "NFLX.MX",
    "EDOARDOB.MX",
    "AGUA.MX",
    "CREAL.MX",
    "ICA.MX",
    "CMOCTEZ.MX",
    "FIBRAPL14.MX",
    "FINN13.MX",
    "ACCELSAB.MX",
    "FVIA16.MX",
    "FSHOP13.MX",
    "IDEALB-1.MX",
    "GMXT.MX",
    "GICSAB.MX",
    "CYDSASAA.MX",
    "CUERVO.MX",
    "GPH1.MX",
    "FNOVA17.MX",
    "ARA.MX",
    "GIGANTE.MX",
    "ICHB.MX",
    "GFMULTIO.MX",
    "CIDMEGA.MX",
    "FINAMEXO.MX",
    "BAFARB.MX",
    "FPLUS16.MX",
    "OHLMEX.MX",
    "DINEA.MX",
    "DINEB.MX",
    "CONVERA.MX",
    "MINSAB.MX",
    "VISTAA.MX",
    "PLANI.MX",
    "VITROA.MX",
    "TRAXIONA.MX",
    "PINFRAL.MX",
    "UNIFINA.MX",
    "STORAGE18.MX",
    "Q.MX",
    "CUERVO.MX"
]

# ============================================================
#               LISTA DE ACCIONES DE EUA (Yahoo)
# ============================================================
acciones_usa = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
    "SPY",
    "QQQ",
    "IWM",
    "DIA",
    "JPM",
    "BAC",
    "WMT",
    "COST",
    "XOM",
    "UNH",
    "JNJ",
    "KO",
    "PG",
    "SOBR",
    "KIDZW",
    "NCL",
    "AMCI",
    "EUDA",
    "MWG",
    "INDP",
    "DVAX",
    "FMFC",
    "SIDU",
    "IZM",
    "EWTX",
    "VCICW",
    "MODD",
    "CNCK",
    "CREV",
    "TEAD",
    "EQ",
    "AGIO",
    "SRXH",
    "GLSI",
    "DRMA",
    "RPTX",
    "BIXIW",
    "TSE",
    "ZSPC",
    "INAB",
    "NCEW",
    "LFMD",
    "MNTS",
    "HURA",
    "ELOG",
    "TCRX",
    "PSNY",
    "TVTX",
    "AZI",
    "AQB",
    "RZLT",
    "NXXT",
    "RAY",
    "KOD",
    "PASG",
    "ETS",
    "YOUL",
    "ASPCU",
    "KALA",
    "CDLX",
    "FERAR",
    "MYO",
    "ZKH",
    "AUID",
    "AIFU",
    "FTHM",
    "UP",
    "FCHL",
    "IMG",
    "AEC",
    "GRAN",
    "PMAX",
    "RMCO",
    "ECDA",
    "CAPT",
    "NEPH",
    "DWTX",
    "BAK",
    "ALVO",
    "AKTX",
    "HCWC",
    "NRXS",
    "TGE",
    "LGCL",
    "MBAVW",
    "AFJK",
    "CRDF",
    "BCTX",
    "CNTY",
    "SKBL",
    "FBYD",
    "MWYN",
    "SATL",
    "IOTR",
    "FEAM",
    "UPC",
    "MAIA",
    "BHM",
    "SMTK",
    "COCH",
    "AZ",
    "VCIG",
    "BW",
    "IMSRW",
    "CCCXW",
    "TVGNW",
    "TISI",
    "FSP",
    "ALMU",
    "PEPG",
    "CV",
    "BCARW",
    "ELVR",
    "TKLF",
    "RDAC",
    "RR",
    "CASI",
    "EJH",
    "TRUG",
    "NMTC",
    "BCAB",
    "SUPX",
    "HTCR",
    "ELLO",
    "VOR",
    "ATLN",
    "YYAI",
    "BNC",
    "SGHT",
    "BRR",
    "METC",
    "PATH",
    "MYSE",
    "FOXX",
    "DDC",
    "QSI",
    "IMDX",
    "RVSN",
    "PMN",
    "ACET",
    "FLD",
    "XFOR",
    "HYPD",
    "PAVS",
    "GLUE",
    "AVX",
    "ALM",
    "LWLG",
    "WETO",
    "AMBO",
    "SGBX",
    "VHC",
    "AHMA",
    "TVGN",
    "ORMP",
    "BIOA",
    "OPAL",
    "ZLAB",
    "TOUR",
    "ASST",
    "SMSI",
    "MYND",
    "LANV",
    "AZTR",
    "ANNA",
    "ALGS",
    "PAMT",
    "INO",
    "LASE",
    "HQI",
    "IMRX",
    "FEIM",
    "RECT",
    "GCO",
    "MIST",
    "SLE",
    "SLSN",
    "COHN",
    "AERO",
    "SMLR",
    "PARK",
    "IPX",
    "CURV",
    "OWLT",
    "LSF",
    "BLUWW",
    "NSRX",
    "AGAE",
    "OFLX",
    "SNGX"
]





