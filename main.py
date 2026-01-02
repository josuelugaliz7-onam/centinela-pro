import os
import time
import requests
import telebot
import pandas as pd
from threading import Thread
from flask import Flask

# --- CONFIGURACIÓN ---
TOKEN = "8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0"
CHAT_ID = "7951954749"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

MONEDAS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]

def calcular_rsi_simple(precios, periods=14):
    df = pd.DataFrame(precios, columns=['c'])
    delta = df['c'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def obtener_datos(simbolo):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval=15m&limit=100"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return [float(k[4]) for k in res.json()] # Solo precios de cierre
        return None
    except:
        return None

@bot.message_handler(commands=['status'])
def status_command(message):
    bot.reply_to(message, "✅ **CENTINELA ONLINE**\nMotor: Binance\nEstado: Vigilando 15m")

@bot.message_handler(commands=['reporte'])
def enviar_reporte(message):
    msg_espera = bot.reply_to(message, "🔍 **Leyendo Binance...**")
    reporte = "📊 **REPORTE 15M**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    for moneda in MONEDAS:
        precios = obtener_datos(moneda)
        if precios:
            rsi_series = calcular_rsi_simple(precios)
            rsi = rsi_series.iloc[-1]
            precio = precios[-1]
            estado = "🟢 COMPRA" if rsi < 30 else "🔴 VENTA" if rsi > 70 else "⚪ NEUTRAL"
            reporte += f"🔹 **{moneda}**\n   RSI: {rsi:.2f} | ${precio}\n   {estado}\n\n"
        else:
            reporte += f"❌ **{moneda}**: Error\n\n"
    bot.edit_message_text(reporte, message.chat.id, msg_espera.message_id, parse_mode="Markdown")

@app.route('/')
def home(): return "Bot Vivo"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
    
