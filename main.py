import os
import time
import requests
import pandas as pd
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home(): 
    return "🛡️ Centinela Pro Online - Vigilando Binance"

def run():
    # Ajuste vital para Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
MONEDAS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT']

IMG_TORO = "https://drive.google.com/uc?export=view&id=1Uss3MV3GfW--lNrDbLOGuZPA4x3QINk7"
IMG_OSO = "https://drive.google.com/uc?export=view&id=1MCs-_fkNnfCLA0knV-CdXlg8-7TRgogF"

def calcular_rsi(serie, periodo=14):
    delta = serie.diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
    pérdida = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
    rs = ganancia / pérdida
    return 100 - (100 / (1+rs))

def enviar_telegram(msg, tipo):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    foto = IMG_TORO if tipo == "compra" else IMG_OSO
    try:
        requests.post(url, data={'chat_id': CHAT_ID, 'caption': msg, 'photo': foto})
    except: print("Error enviando a Telegram")

def analizar():
    for m in MONEDAS:
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={m}&interval=15m&limit=100"
            res = requests.get(url).json()
            df = pd.DataFrame(res, columns=['ts','o','h','l','c','v','ct','qv','nt','tbv','tqv','i'])
            df['c'] = df['c'].astype(float)
            rsi_actual = calcular_rsi(df['c']).iloc[-1]
            precio = df['c'].iloc[-1]

            if rsi_actual < 30:
                enviar_telegram(f"🐂 *COMPRA {m}*\n💰 Precio: ${precio}\n📊 RSI: {rsi_actual:.2f}", "compra")
            elif rsi_actual > 70:
                enviar_telegram(f"🐻 *VENTA {m}*\n💰 Precio: ${precio}\n📊 RSI: {rsi_actual:.2f}", "venta")
            
            print(f"✅ {m} analizada. RSI: {rsi_actual:.2f}")
            time.sleep(2)
        except Exception as e:
            print(f"Error en {m}: {e}")

if __name__ == "__main__":
    keep_alive()
    # Esto hará que el bot analice apenas se encienda
    Thread(target=analizar).start() 
    bot.polling(none_stop=True)
    
    
