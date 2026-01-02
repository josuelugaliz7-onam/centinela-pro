import os
import time
import requests
import telebot
import pandas as pd
import pandas_ta as ta
from threading import Thread
from flask import Flask

# --- CONFIGURACIÓN ---
TOKEN = "8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0" # Asegúrate de que tu token esté correcto
CHAT_ID = "7951954749"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

MONEDAS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOTUSDT",
    "MATICUSDT", "LINKUSDT", "AVAXUSDT", "XRPUSDT", "LTCUSDT"
]

IMG_TORO = "https://i.ibb.co/Lkv7Lp8/toro.jpg"
IMG_OSO = "https://i.ibb.co/S7X7Y9v/oso.jpg"

stats = {"compras": 0, "ventas": 0}

# --- LÓGICA TÉCNICA ---
def calcular_stoch_rsi(data):
    df = pd.DataFrame(data, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ts_e', 'qv', 'nt', 'tbv', 'tqv', 'i'])
    df['c'] = df['c'].astype(float)
    # Fórmula exacta: 3, 3, 14, 14
    stoch = ta.stochrsi(df['c'], length=14, rsi_length=14, k=3, d=3)
    last_k = stoch.iloc[-1][0]
    last_d = stoch.iloc[-1][1]
    return last_k, last_d

def escaneo_continuo():
    global stats
    print("SISTEMA DE ESCANEO INICIADO 🚀")
    while True:
        for moneda in MONEDAS:
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={moneda}&interval=15m&limit=100"
                res = requests.get(url)
                data = res.json()
                k, d = calcular_stoch_rsi(data)
                
                # Ajuste de sensibilidad a 25/75 para capturar el movimiento actual
                if k < 25:
                    msg = f"🟢 **TORO DETECTADO en {moneda}**\n\nStoch RSI (K): {k:.2f}\nEstado: SOBREVENTA"
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode="Markdown")
                    stats["compras"] += 1
                    time.sleep(5)
                elif k > 75:
                    msg = f"🔴 **OSO DETECTADO en {moneda}**\n\nStoch RSI (K): {k:.2f}\nEstado: SOBRECOMPRA"
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode="Markdown")
                    stats["ventas"] += 1
                    time.sleep(5)
            except Exception as e:
                print(f"Error analizando {moneda}: {e}")
        time.sleep(60)

# --- COMANDOS TELEGRAM ---
@bot.message_handler(commands=['status'])
def enviar_status(message):
    respuesta = (
        f"¡ACTIVO JEFE 😎!\n\n"
        f"Hoy llevo:\n"
        f"🟢 {stats['compras']} Compras\n"
        f"🔴 {stats['ventas']} Ventas"
    )
    bot.reply_to(message, respuesta)

# --- RUTAS WEB ---
@app.route('/')
def home():
    return "Centinela Pro en ejecución..."

def run_web():
    app.run(host='0.0.0.0', port=8080)

# --- INICIO ---
if __name__ == "__main__":
    # Hilo para el servidor web (Flask)
    t_web = Thread(target=run_web)
    t_web.start()
    
    # Hilo para el análisis de mercado
    t_scan = Thread(target=escaneo_continuo)
    t_scan.start()
    
    # Ejecutar el bot de Telegram
    print("Bot de Telegram esperando órdenes...")
    bot.infinity_polling()
    
