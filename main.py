import telebot
import time
import requests
import pandas as pd
import threading
from flask import Flask # Añadimos esto para engañar a Render

# --- CONFIGURACIÓN DEL SERVIDOR WEB ---
app = Flask('')

@app.route('/')
def home():
    return "Centinela Pro está Vivo y Patrullando! 🚀"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# --- TU BOT ORIGINAL ---
TOKEN = '8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0'
CHAT_ID = '7951954749'
bot = telebot.TeleBot(TOKEN)

MONEDAS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'RNDRUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT', 'NEARUSDT']
IMG_TORO = 'https://raw.githubusercontent.com/josuelugaliz7-onam/centinela-pro/main/toro.jpg'
IMG_OSO = 'https://raw.githubusercontent.com/josuelugaliz7-onam/centinela-pro/main/oso.jpg'

def analizar_mercado():
    while True:
        for moneda in MONEDAS:
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={moneda}&interval=15m&limit=100"
                data = requests.get(url).json()
                precios = pd.DataFrame(data)[4].astype(float)
                
                period = 14
                delta = precios.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                valor_rsi = rsi.iloc[-1]
                precio_actual = precios.iloc[-1]
                
                if valor_rsi < 20:
                    msg = f"🟢 **COMPRA: {moneda}**\nRSI: {valor_rsi:.2f}\nPrecio: ${precio_actual}"
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode='Markdown')
                elif valor_rsi > 80:
                    msg = f"🔴 **VENTA: {moneda}**\nRSI: {valor_rsi:.2f}\nPrecio: ${precio_actual}"
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode='Markdown')
            except:
                continue
        time.sleep(900)

@bot.message_handler(commands=['status', 'hola'])
def enviar_status(message):
    bot.reply_to(message, "¡ACTIVO JEFE 😎 estoy Vivo y Patrullando!")

if __name__ == "__main__":
    # 1. Iniciamos el servidor web para Render
    threading.Thread(target=run_web_server, daemon=True).start()
    # 2. Iniciamos el análisis de mercado
    threading.Thread(target=analizar_mercado, daemon=True).start()
    # 3. Iniciamos el bot de Telegram
    bot.send_message(CHAT_ID, "🚀 Centinela con Anti-Suspensión activado, Jefe.")
    bot.polling(none_stop=True)
    
