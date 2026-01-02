import os
import time
import requests
import telebot
import pandas as pd
import pandas_ta as ta
from threading import Thread
from flask import Flask

# --- CONFIGURACIÓN ---
TOKEN = "8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0"
CHAT_ID = "7951954749"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Nombres de símbolos para Binance
MONEDAS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]

IMG_TORO = "https://i.ibb.co/Lkv7Lp8/toro.jpg"
IMG_OSO = "https://i.ibb.co/S7X7Y9v/oso.jpg"

def obtener_datos_binance(simbolo):
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval=15m&limit=100"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            df = pd.DataFrame(res.json(), columns=['t','o','h','l','c','v','T','q','n','V','Q','B'])
            return df['c'].astype(float)
        return None
    except:
        return None

def escaneo_continuo():
    print("🚀 PATRULLAJE BINANCE INICIADO")
    while True:
        for moneda in MONEDAS:
            precios = obtener_datos_binance(moneda)
            if precios is not None:
                stoch = ta.stochrsi(precios, length=14, rsi_length=14, k=3, d=3)
                k = stoch.iloc[-1][0]
                precio_actual = precios.iloc[-1]

                if k < 20:
                    msg = f"🟢 **TORO: {moneda}**\n📊 RSI: {k:.2f}\n💰 ${precio_actual}"
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode="Markdown")
                    time.sleep(5)
                elif k > 80:
                    msg = f"🔴 **OSO: {moneda}**\n📊 RSI: {k:.2f}\n💰 ${precio_actual}"
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode="Markdown")
                    time.sleep(5)
        time.sleep(60)

@bot.message_handler(commands=['reporte'])
def enviar_reporte(message):
    msg_espera = bot.reply_to(message, "🔍 **Consultando Binance...**")
    reporte = "📊 **REPORTE BINANCE (15M)**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    for moneda in MONEDAS:
        precios = obtener_datos_binance(moneda)
        if precios is not None:
            stoch = ta.stochrsi(precios, length=14, rsi_length=14, k=3, d=3)
            k = stoch.iloc[-1][0]
            estado = "🟢 COMPRA" if k < 20 else "🔴 VENTA" if k > 80 else "⚪ NEUTRAL"
            reporte += f"🔹 **{moneda}**: {k:.2f} | {estado}\n"
        else:
            reporte += f"❌ **{moneda}**: Error\n"
    bot.edit_message_text(reporte, message.chat.id, msg_espera.message_id, parse_mode="Markdown")

@app.route('/')
def home(): return "Centinela Binance Activo"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    Thread(target=escaneo_continuo).start()
    bot.infinity_polling()
    
