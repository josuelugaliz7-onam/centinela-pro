import os
import time
import requests
import telebot
import pandas as pd
import pandas_ta as ta
from threading import Thread
from flask import Flask
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = "8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0"
CHAT_ID = "7951954749"
# Tu nueva API Key de CoinGecko
API_KEY_GECKO = "CG-V3U4XF8HDAiNqKi9Td2ijoGE" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

MONEDAS = ["bitcoin", "ethereum", "solana", "ripple", "dogecoin"]

IMG_TORO = "https://i.ibb.co/Lkv7Lp8/toro.jpg"
IMG_OSO = "https://i.ibb.co/S7X7Y9v/oso.jpg"

stats = {"compras": 0, "ventas": 0, "detalles": {m: {"c": 0, "v": 0} for m in MONEDAS}}

def obtener_datos(moneda):
    url = f"https://api.coingecko.com/api/v3/coins/{moneda}/market_chart?vs_currency=usd&days=1&interval=m1"
    headers = {"x-cg-demo-api-key": API_KEY_GECKO}
    try:
        # Pequeño retraso preventivo para estabilidad
        time.sleep(1.2)
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return pd.DataFrame([p[1] for p in res.json()['prices']], columns=['c'])
        return None
    except:
        return None

def escaneo_continuo():
    global stats
    print("🚀 PATRULLAJE BLINDADO INICIADO")
    while True:
        for moneda in MONEDAS:
            df = obtener_datos(moneda)
            if df is not None:
                try:
                    stoch = ta.stochrsi(df['c'], length=14, rsi_length=14, k=3, d=3)
                    k = stoch.iloc[-1][0]
                    precio_actual = df['c'].iloc[-1]

                    if k < 20:
                        msg = f"🟢 **TORO DETECTADO: {moneda.upper()}**\n\n📊 RSI: {k:.2f}\n💰 Precio: ${precio_actual:.4f}"
                        bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode="Markdown")
                        stats["compras"] += 1
                        time.sleep(5)
                    elif k > 80:
                        msg = f"🔴 **OSO DETECTADO: {moneda.upper()}**\n\n📊 RSI: {k:.2f}\n💰 Precio: ${precio_actual:.4f}"
                        bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode="Markdown")
                        stats["ventas"] += 1
                        time.sleep(5)
                except: continue
        
        time.sleep(60) # VELOCIDAD AJUSTADA PARA ESTABILIDAD

@bot.message_handler(commands=['status'])
def status_command(message):
    bot.reply_to(message, "🧑‍💻 **¡CENTINELA ONLINE!**\nPatrullando con API Key.\nFrecuencia: 60s.")

@bot.message_handler(commands=['reporte'])
def enviar_reporte(message):
    msg_espera = bot.reply_to(message, "🔍 **Generando Reporte con API Key...**")
    reporte = "📊 **REPORTE DE MERCADO (15M)**\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
    
    for moneda in MONEDAS:
        df = obtener_datos(moneda)
        if df is not None:
            stoch = ta.stochrsi(df['c'], length=14, rsi_length=14, k=3, d=3)
            k = stoch.iloc[-1][0]
            precio = df['c'].iloc[-1]
            estado = "🟢 COMPRA" if k < 20 else "🔴 VENTA" if k > 80 else "⚪ NEUTRAL"
            reporte += f"🔹 **{moneda.upper()}**\n   {k:.2f} | ${precio:.2f} | {estado}\n\n"
        else:
            reporte += f"❌ **{moneda.upper()}**: Error API\n\n"
            
    bot.edit_message_text(reporte, message.chat.id, msg_espera.message_id, parse_mode="Markdown")

@app.route('/')
def home(): return "Centinela Activo"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    Thread(target=escaneo_continuo).start()
    bot.infinity_polling()
