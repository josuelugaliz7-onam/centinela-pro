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
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Solo las 5 más importantes y estables
MONEDAS = ["bitcoin", "ethereum", "solana", "ripple", "dogecoin"]

IMG_TORO = "https://i.ibb.co/Lkv7Lp8/toro.jpg"
IMG_OSO = "https://i.ibb.co/S7X7Y9v/oso.jpg"

stats = {"compras": 0, "ventas": 0, "detalles": {m: {"c": 0, "v": 0} for m in MONEDAS}}

def obtener_datos(moneda):
    # Pedimos datos de 1 minuto para máxima precisión
    url = f"https://api.coingecko.com/api/v3/coins/{moneda}/market_chart?vs_currency=usd&days=1&interval=m1"
    res = requests.get(url, timeout=10)
    return pd.DataFrame([p[1] for p in res.json()['prices']], columns=['c'])

def escaneo_continuo():
    global stats
    print("🚀 PATRULLAJE DE ALTA VELOCIDAD INICIADO")
    while True:
        for moneda in MONEDAS:
            try:
                df = obtener_datos(moneda)
                # Cálculo puro de Stoch RSI
                stoch = ta.stochrsi(df['c'], length=14, rsi_length=14, k=3, d=3)
                
                precio_actual = df['c'].iloc[-1]
                k = stoch.iloc[-1][0]

                # SEÑAL DE COMPRA 🟢 (Sobreventa < 20)
                if k < 20:
                    msg = (f"🟢 **TORO DETECTADO: {moneda.upper()}**\n\n"
                           f"📊 RSI Stoch: {k:.2f}\n"
                           f"💰 Precio: ${precio_actual:.4f}\n"
                           f"🎯 TP (1.5%): ${precio_actual * 1.015:.4f}\n"
                           f"🛑 SL (1.0%): ${precio_actual * 0.99:.4f}")
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode="Markdown")
                    stats["compras"] += 1
                    stats["detalles"][moneda]["c"] += 1
                    time.sleep(5) # Evitar spam de la misma señal

                # SEÑAL DE VENTA 🔴 (Sobrecompra > 80)
                elif k > 80:
                    msg = (f"🔴 **OSO DETECTADO: {moneda.upper()}**\n\n"
                           f"📊 RSI Stoch: {k:.2f}\n"
                           f"💰 Precio: ${precio_actual:.4f}\n"
                           f"🎯 TP (1.5%): ${precio_actual * 0.985:.4f}\n"
                           f"🛑 SL (1.0%): ${precio_actual * 1.01:.4f}")
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode="Markdown")
                    stats["ventas"] += 1
                    stats["detalles"][moneda]["v"] += 1
                    time.sleep(5)

            except: continue
        
        # Resumen Diario 9:00 PM
        ahora = datetime.now()
        if ahora.hour == 21 and ahora.minute == 0:
            resumen = "📋 **RESUMEN DIARIO DE CAZA**\n\n"
            for m, s in stats["detalles"].items():
                resumen += f"🔹 {m.capitalize()}: 🟢 {s['c']} | 🔴 {s['v']}\n"
            bot.send_message(CHAT_ID, resumen, parse_mode="Markdown")
            stats = {"compras": 0, "ventas": 0, "detalles": {m: {"c": 0, "v": 0} for m in MONEDAS}}
            time.sleep(60)

        time.sleep(20) # REVISIÓN CADA 20 SEGUNDOS

@bot.message_handler(commands=['status'])
def status_command(message):
    bot.reply_to(message, f"🧑‍💻 **¡ACTIVO JEFE!**\nPatrullando 5 monedas cada 20s.\n\n🟢 {stats['compras']} | 🔴 {stats['ventas']}", parse_mode="Markdown")

@app.route('/')
def home(): return "Centinela Activo"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    Thread(target=escaneo_continuo).start()
    bot.infinity_polling()
                    
