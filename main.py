import telebot
import time
import requests
import pandas as pd
import threading
from flask import Flask
from datetime import datetime

# --- CONFIGURACIÓN ---
app = Flask('')
TOKEN = '8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0'
CHAT_ID = '7951954749'
bot = telebot.TeleBot(TOKEN)

MONEDAS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'RNDRUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT', 'NEARUSDT']
IMG_TORO = 'https://raw.githubusercontent.com/josuelugaliz7-onam/centinela-pro/main/toro.jpg'
IMG_OSO = 'https://raw.githubusercontent.com/josuelugaliz7-onam/centinela-pro/main/oso.jpg'

# Contadores para el resumen diario
stats = {"compras": 0, "ventas": 0, "fecha": datetime.now().date()}

@app.route('/')
def home():
    return "Centinela Pro: Sistema Anti-Suspensión Activo 🚀"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def calcular_stoch_rsi(data, period=14, smoothK=3, smoothD=3):
    prices = pd.DataFrame(data)[4].astype(float)
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    stoch_rsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    k = stoch_rsi.rolling(smoothK).mean() * 100
    d = k.rolling(smoothD).mean()
    return k.iloc[-1], d.iloc[-1]

def analizar_mercado():
    global stats
    while True:
        # Verificar si cambió el día para enviar resumen
        hoy = datetime.now().date()
        if hoy > stats["fecha"]:
            reporte = f"📊 **RESUMEN DIARIO DEL CENTINELA**\n\n🟢 Señales de Compra: {stats['compras']}\n🔴 Señales de Venta: {stats['ventas']}\n\n¡Mañana vamos por más! 🚀"
            bot.send_message(CHAT_ID, reporte, parse_mode='Markdown')
            stats = {"compras": 0, "ventas": 0, "fecha": hoy}

        for moneda in MONEDAS:
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={moneda}&interval=15m&limit=100"
                data = requests.get(url).json()
                k, d = calcular_stoch_rsi(data)
                precio = data[-1][4]
                
                # Lógica de señales (Cruce de 20 y 80)
                if k < 20:
                    msg = f"🟢 **TORO DETECTADO en {moneda}**\nStoch RSI (K): {k:.2f}\nPrecio: ${precio}"
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode='Markdown')
                    stats["compras"] += 1
                    time.sleep(10) # Evitar spam
                elif k > 80:
                    msg = f"🔴 **OSO DETECTADO en {moneda}**\nStoch RSI (K): {k:.2f}\nPrecio: ${precio}"
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode='Markdown')
                    stats["ventas"] += 1
                    time.sleep(10)
            except:
                continue
        time.sleep(60) # Revisar cada 1 minuto

@bot.message_handler(commands=['status'])
def enviar_status(message):
    reporte_actual = f"¡ACTIVO JEFE 😎!\n\nHoy llevo:\n🟢 {stats['compras']} Compras\n🔴 {stats['ventas']} Ventas"
    bot.reply_to(message, reporte_actual)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    threading.Thread(target=analizar_mercado, daemon=True).start()
    bot.polling(none_stop=True)
                
