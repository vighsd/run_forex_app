import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# Forex pairs list
forex_pairs = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X",
    "EURGBP=X", "EURJPY=X", "EURAUD=X", "EURCAD=X", "EURCHF=X", "EURNZD=X",
    "GBPJPY=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X", "GBPNZD=X",
    "AUDJPY=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X",
    "CADJPY=X", "CADCHF=X", "NZDJPY=X", "NZDCAD=X"
]

def get_data(pair):
    data = yf.Ticker(pair).history(period="60d")
    if data.empty or len(data) < 35:
        return None
    return data

def momentum_sma_strategy(data):
    close = data['Close']
    momentum = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]
    sma_short = close.iloc[-3:].mean()
    sma_long = close.iloc[-10:].mean()
    trend = 1 if sma_short > sma_long else -1
    score = momentum * trend
    direction = "Long" if score > 0 else "Short"
    entry = close.iloc[-1]
    return direction, entry, score

def ema_crossover_strategy(data):
    close = data['Close']
    ema_short = close.ewm(span=12).mean()
    ema_long = close.ewm(span=26).mean()
    if ema_short.iloc[-2] < ema_long.iloc[-2] and ema_short.iloc[-1] > ema_long.iloc[-1]:
        direction = "Long"
        score = ema_short.iloc[-1] - ema_long.iloc[-1]
    elif ema_short.iloc[-2] > ema_long.iloc[-2] and ema_short.iloc[-1] < ema_long.iloc[-1]:
        direction = "Short"
        score = ema_long.iloc[-1] - ema_short.iloc[-1]
    else:
        return None, None, 0
    entry = close.iloc[-1]
    return direction, entry, score

def rsi_strategy(data):
    close = data['Close']
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean().iloc[-1]
    avg_loss = loss.rolling(14).mean().iloc[-1]
    if avg_loss == 0:
        return None, None, 0
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    entry = close.iloc[-1]

    if rsi < 30:
        direction = "Long"
        score = 30 - rsi  # Stronger when lower RSI
    elif rsi > 70:
        direction = "Short"
        score = rsi - 70  # Stronger when higher RSI
    else:
        return None, None, 0
    return direction, entry, score

def macd_strategy(data):
    close = data['Close']
    ema_12 = close.ewm(span=12).mean()
    ema_26 = close.ewm(span=26).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9).mean()
    if macd.iloc[-2] < signal.iloc[-2] and macd.iloc[-1] > signal.iloc[-1]:
        direction = "Long"
        score = macd.iloc[-1] - signal.iloc[-1]
    elif macd.iloc[-2] > signal.iloc[-2] and macd.iloc[-1] < signal.iloc[-1]:
        direction = "Short"
        score = signal.iloc[-1] - macd.iloc[-1]
    else:
        return None, None, 0
    entry = close.iloc[-1]
    return direction, entry, score

def calculate_trade_levels(entry_price, direction, sl_pct=0.01):
    if direction == "Long":
        sl = entry_price * (1 - sl_pct)
        tp = entry_price * (1 + sl_pct * 3)
    else:  # Short
        sl = entry_price * (1 + sl_pct)
        tp = entry_price * (1 - sl_pct * 3)
    risk = abs(entry_price - sl)
    return round(sl, 5), round(tp, 5), round(risk, 5)

def get_sample_news_events():
    now = datetime.utcnow()
    news_events = [
        {
            "datetime": now + timedelta(hours=1),
            "currency": "USD",
            "impact": "High",
            "event": "Non-Farm Payrolls",
            "actual": 210000,
            "forecast": 180000,
            "previous": 200000
        },
        {
            "datetime": now + timedelta(hours=3),
            "currency": "EUR",
            "impact": "Medium",
            "event": "ECB Interest Rate Decision",
            "actual": 0.75,
            "forecast": 0.50,
            "previous": 0.50
        },
        {
            "datetime": now + timedelta(hours=22),
            "currency": "JPY",
            "impact": "Low",
            "event": "Trade Balance",
            "actual": 1.2,
            "forecast": 1.5,
            "previous": 1.3
        },
        {
            "datetime": now + timedelta(hours=26),  # Outside 24h range
            "currency": "GBP",
            "impact": "High",
            "event": "BoE Inflation Report",
            "actual": None,
            "forecast": None,
            "previous": None
        }
    ]
    return news_events

def filter_news_next_24h(news_events):
    now = datetime.utcnow()
    cutoff = now + timedelta(hours=24)
    return [news for news in news_events if now <= news["datetime"] <= cutoff]

# Market predictions and economic papers links
daily_market_predictions = [
    {
        "title": "Daily Forex Market Outlook",
        "link": "https://www.dailyfx.com/forex-market-news"
    },
    {
        "title": "Forex Economic Forecast",
        "link": "https://www.fxstreet.com/economic-calendar"
    },
    {
        "title": "Investing.com Forex News",
        "link": "https://www.investing.com/forex/news"
    }
]

important_economic_papers = [
    {
        "title": "BIS Quarterly Review",
        "link": "https://www.bis.org/publ/qtrpdf/r_qt2212.htm"
    },
    {
        "title": "IMF Global Financial Stability Report",
        "link": "https://www.imf.org/en/Publications/GFSR"
    },
    {
        "title": "OECD Economic Outlook",
        "link": "https://www.oecd.org/economic-outlook/"
    }
]

# YouTube channels for Forex news & analysis
youtube_channels = [
    {
        "name": "Bloomberg Markets and Finance",
        "link": "https://www.youtube.com/user/Bloomberg"
    },
    {
        "name": "ForexSignals TV",
        "link": "https://www.youtube.com/c/ForexSignalsTV"
    },
    {
        "name": "DailyFX - Forex Trading News",
        "link": "https://www.youtube.com/c/DailyFX"
    },
    {
        "name": "The Trading Channel",
        "link": "https://www.youtube.com/c/TheTradingChannel"
    },
    {
        "name": "Investing.com",
        "link": "https://www.youtube.com/user/investingdotcom"
    }
]

st.set_page_config(page_title="Forex Trading Dashboard", layout="wide")

st.title("Forex Trading Dashboard")

tab = st.tabs(["Strategies", "News", "Extras"])

# --- Strategies Tab ---
with tab[0]:
    st.header("Top 5 Trades by Strategy (Intraday)")
    strategies = {
        "Momentum + SMA Crossover": momentum_sma_strategy,
        "EMA Crossover": ema_crossover_strategy,
        "RSI Oversold/Overbought": rsi_strategy,
        "MACD Crossover": macd_strategy
    }

    for strat_name, strat_func in strategies.items():
        st.subheader(strat_name)
        results = []
        for pair in forex_pairs:
            data = get_data(pair)
            if data is None:
                continue
            direction, entry, score = strat_func(data)
            if direction is None or score == 0:
                continue
            sl, tp, risk = calculate_trade_levels(entry, direction)
            results.append({
                "Pair": pair.replace("=X", ""),
                "Direction": direction,
                "Entry": round(entry, 5),
                "Stop Loss": sl,
                "Take Profit": tp,
                "Score": round(score, 5),
                "Risk": risk
            })
        if not results:
            st.write("No signals found for this strategy.")
            continue

        # Sort by absolute score descending and pick top 5
        top_trades = sorted(results, key=lambda x: abs(x["Score"]), reverse=True)[:5]
        st.table(top_trades)


# --- News Tab ---
with tab[1]:
    st.header("Forex Economic News - Next 24 Hours")
    news_events = get_sample_news_events()
    filtered_news = filter_news_next_24h(news_events)
    
    if not filtered_news:
        st.write("No high-impact news events in the next 24 hours.")
    else:
        for news in filtered_news:
            dt_local = news["datetime"].strftime("%Y-%m-%d %H:%M UTC")
            st.subheader(f"{news['event']} ({news['impact']} impact)")
            st.write(f"Currency: {news['currency']}")
            st.write(f"Scheduled Time: {dt_local}")
            st.write(f"Actual: {news['actual']}")
            st.write(f"Forecast: {news['forecast']}")
            st.write(f"Previous: {news['previous']}")
            st.markdown("---")


# --- Extras Tab ---
with tab[2]:
    st.header("Daily Market Predictions & Key Resources")

    st.subheader("Daily Market Predictions")
    for pred in daily_market_predictions:
        st.markdown(f"- [{pred['title']}]({pred['link']})")

    st.subheader("Important Economic Papers")
    for paper in important_economic_papers:
        st.markdown(f"- [{paper['title']}]({paper['link']})")

    st.subheader("YouTube Channels for Morning Forex News & Analysis")
    for channel in youtube_channels:
        st.markdown(f"- [{channel['name']}]({channel['link']})")

    st.markdown("---")
    st.markdown("**Tip:** Check these channels early in your day for fresh market insights and updates.")

