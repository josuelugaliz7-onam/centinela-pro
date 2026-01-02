import os
import time
import requests
import telebot
from threading import Thread
from flask import Flask

# --- CONFIGURACIÓN ---
TOKEN = "8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0"
CHAT_ID = "7951954749"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

MONEDAS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"]

def calcular_rsi_manual(precios, period=14):
    if len(precios) < period + 1: return 50
    gains, losses = [], []
    for i in range(1, len(precios)):
        diff = precios[i] - precios[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def obtener_precio_y_rsi(simbolo):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={simbolo}&interval=15m&limit=50"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            datos = res.json()
            cierres = [float(vela[4]) for vela in datos]
            rsi = calcular_rsi_manual(cierres)
            return cierres[-1], rsi
        return None, None
    except:
        return None, None

@bot.message_handler(commands=['status'])
def status_command(message):
    bot.reply_to(message, "✅ **CENTINELA ONLINE**\nMotor: Binance Nativo\nListo para /reporte")

@bot.message_handler(commands=['reporte'])
def enviar_reporte(message):
    msg_espera = bot.reply_to(message, "🔍 **Consultando Binance...**")
    reporte = "📊 **REPORTE 15M (NATIVO)**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    for moneda in MONEDAS:
        precio, rsi = obtener_precio_y_rsi(moneda)
        if precio:
            estado = "🟢 COMPRA" if rsi < 30 else "🔴 VENTA" if rsi > 70 else "⚪ NEUTRAL"
            reporte += f"🔹 **{moneda}**\n   RSI: {rsi:.2f} | ${precio}\n   {estado}\n\n"
        else:
            reporte += f"❌ **{moneda}**: Error conexión\n\n"
    bot.edit_message_text(reporte, message.chat.id, msg_espera.message_id, parse_mode="Markdown")

@app.route('/')
def home(): return "Bot Vivo"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    bot.infinity_polling()
    
