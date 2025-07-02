import os, asyncio, requests, pandas as pd
from quotexapi.stable import Quotex
import pandas_ta as ta

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TG_TOKEN = os.getenv("TG_TOKEN")
TG_USER_ID = os.getenv("TG_USER_ID")

ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'EURUSD-OTC', 'GBPUSD-OTC', 'USDJPY-OTC', 'AUDUSD-OTC']
TIMEFRAME = 1
TRADE_EXPIRY = 2

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": TG_USER_ID, "text": message}
    try:
        requests.post(url, data=data)
    except: pass

last_signals = []

def generate_signal(df):
    df['ema20'] = ta.ema(df['close'], length=20)
    df['ema50'] = ta.ema(df['close'], length=50)
    df['rsi'] = ta.rsi(df['close'], length=14)
    df['macd'] = ta.macd(df['close'])['MACD_12_26_9']
    latest = df.iloc[-1]
    if latest['ema20'] > latest['ema50'] and latest['rsi'] < 70 and latest['macd'] > 0:
        return "CALL"
    elif latest['ema20'] < latest['ema50'] and latest['rsi'] > 30 and latest['macd'] < 0:
        return "PUT"
    return None

async def run_bot():
    from web_dashboard import update_signals
    qx = Quotex()
    await qx.connect()
    await qx.login(EMAIL, PASSWORD)
    while True:
        for asset in ASSETS:
            candles = await qx.get_candles(asset, TIMEFRAME, 100)
            df = pd.DataFrame(candles)
            df['close'] = df['close'].astype(float)
            signal = generate_signal(df)
            if signal:
                msg = f"📡 Quotex Signal
Pair: {asset}
Direction: {signal}
Timeframe: {TIMEFRAME}M
Expiry: {TRADE_EXPIRY}M"
                send_telegram(msg)
                last_signals.append({"asset": asset, "signal": signal})
                update_signals(last_signals[-5:])
        await asyncio.sleep(60)

def start_bot():
    asyncio.run(run_bot())