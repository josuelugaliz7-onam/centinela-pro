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

# Monedas seleccionadas (Estables y de alta volatilidad)
MONEDAS = ["ethereum", "bitcoin", "ripple", "dogecoin", "solana", "cardano", "polkadot", "matic-network", "chainlink", "avalanche-2"]

IMG_TORO = "https://i.ibb.co/Lkv7Lp8/toro.jpg"
IMG_OSO = "https://i.ibb.co/S7X7Y9v/oso.jpg"

# Memoria del Bot
stats = {"compras": 0, "ventas": 0, "detalles": {m: {"c": 0, "v": 0} for m in MONEDAS}}

def obtener_datos(moneda):
    url = f"https://api.coingecko.com/api/v3/coins/{moneda}/market_chart?vs_currency=usd&days=1&interval=m1"
    res = requests.get(url, timeout=15)
    df = pd.DataFrame([p[1] for p in res.json()['prices']], columns=['c'])
    return df

def escaneo_continuo():
    global stats
    while True:
        for moneda in MONEDAS:
            try:
                df = obtener_datos(moneda)
                stoch = ta.stochrsi(df['c'], length=14, rsi_length=14, k=3, d=3)
                bb = ta.bbands(df['c'], length=20, std=2)
                
                precio_actual = df['c'].iloc[-1]
                k = stoch.iloc[-1][0]
                bb_inf = bb.iloc[-1][0]
                bb_sup = bb.iloc[-1][2]

                # LÓGICA DE COMPRA
                if k < 20 and precio_actual <= bb_inf:
                    tp = precio_actual * 1.015
                    sl = precio_actual * 0.99
                    msg = (f"🟢 **TORO DETECTADO: {moneda.upper()}**\n\n"
                           f"📊 RSI Stoch: {k:.2f}\n"
                           f"💰 Entrada: ${precio_actual:.4f}\n"
                           f"🎯 TP: ${tp:.4f}\n"
                           f"🛑 SL: ${sl:.4f}")
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode="Markdown")
                    stats["compras"] += 1
                    stats["detalles"][moneda]["c"] += 1

                # LÓGICA DE VENTA
                elif k > 80 and precio_actual >= bb_sup:
                    tp = precio_actual * 0.985
                    sl = precio_actual * 1.01
                    msg = (f"🔴 **OSO DETECTADO: {moneda.upper()}**\n\n"
                           f"📊 RSI Stoch: {k:.2f}\n"
                           f"💰 Entrada: ${precio_actual:.4f}\n"
                           f"🎯 TP: ${tp:.4f}\n"
                           f"🛑 SL: ${sl:.4f}")
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode="Markdown")
                    stats["ventas"] += 1
                    stats["detalles"][moneda]["v"] += 1

            except Exception as e: print(f"Error en {moneda}: {e}")
            time.sleep(5)

        # --- RESUMEN DIARIO 9:00 PM ---
        ahora = datetime.now()
        if ahora.hour == 21 and ahora.minute == 0:
            resumen = "📋 **RESUMEN DIARIO DE CAZA**\n\n"
            for m, s in stats["detalles"].items():
                resumen += f"🔸 {m.capitalize()}: 🟢 {s['c']} | 🔴 {s['v']}\n"
            
            resumen += f"\n**TOTAL DEL DÍA:**\n🟢 {stats['compras']} Compras\n🔴 {stats['ventas']} Ventas"
            bot.send_message(CHAT_ID, resumen, parse_mode="Markdown")
            
            # Reiniciar contadores para el día siguiente
            stats = {"compras": 0, "ventas": 0, "detalles": {m: {"c": 0, "v": 0} for m in MONEDAS}}
            time.sleep(60)
            
        time.sleep(60)

# --- COMANDOS TELEGRAM ---
@bot.message_handler(commands=['status'])
def status_command(message):
    respuesta = (
        f"🧑‍💻 **¡ACTIVO JEFE!**\n"
        f"Estoy patrullando hasta ahora.\n\n"
        f"**VAMOS:**\n"
        f"🟢 {stats['compras']} Compras detectadas\n"
        f"🔴 {stats['ventas']} Ventas detectadas"
    )
    bot.reply_to(message, respuesta, parse_mode="Markdown")

@app.route('/')
def home(): return "Centinela Activo"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    Thread(target=escaneo_continuo).start()
    bot.infinity_polling()
    
