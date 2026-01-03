import os
import time
import telebot
from binance.client import Client
import pandas_ta as ta
import pandas as pd
import schedule
import threading

# --- CONFIGURACIÓN DE CREDENCIALES ---
TOKEN = '8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0'
CHAT_ID = '7951954749'
API_KEY = 'XdSO34fcveUT28hE8EygJbMW0AtzFxhJVidhqhE3UyRSIUHiXqddQVs7VZqcH52K'
API_SECRET = 'IYz86JkkcjiC3Mjm0DMD1zz8lbtzATBHdUTzm8C3K0JXLqQHFhhfWZ68hDlmosty'

bot = telebot.TeleBot(TOKEN)
# Forzamos el uso de un servidor alternativo para evitar bloqueos de ubicación
client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://api1.binance.com/api'

# --- VARIABLES GLOBALES (CACHÉ Y CONTEO) ---
ultimo_analisis = {"precio": 0, "rsi": 0, "tiempo": "Esperando datos..."}
conteo_reporte = {"compras": 0, "ventas": 0}

# --- FUNCIONES DE ANÁLISIS ---
def obtener_datos_eth():
    global ultimo_analisis
    try:
        # Pedimos 100 velas de 15m
        candles = client.get_klines(symbol='ETHUSDT', interval=Client.KLINE_INTERVAL_15MINUTE, limit=100)
        df = pd.DataFrame(candles, columns=['ts', 'o', 'h', 'l', 'c', 'v', 'ct', 'qv', 'nt', 'tb', 'tg', 'i'])
        df['close'] = df['c'].astype(float)
        
        # Cálculo de Stoch RSI
        stoch = ta.stochrsi(df['close'], length=14, rsi_length=14, k=3, d=3)
        rsi_k = stoch['STOCHRSIk_14_14_3_3'].iloc[-1]
        precio_actual = df['close'].iloc[-1]
        
        ultimo_analisis = {
            "precio": precio_actual,
            "rsi": rsi_k,
            "tiempo": time.strftime("%H:%M:%S")
        }
        return rsi_k, precio_actual
    except Exception as e:
        print(f"Error Binance: {e}")
        return None, None

# --- COMANDOS DE TELEGRAM ---
@bot.message_handler(commands=['status'])
def enviar_status(message):
    global ultimo_analisis
    resumen = (f"📊 **ESTADO DE ETH (Caché)**\n\n"
               f"💰 Precio: ${ultimo_analisis['precio']}\n"
               f"🧑‍💻 RSI Stoch: {ultimo_analisis['rsi']:.2f}\n"
               f"🕒 Actualizado: {ultimo_analisis['tiempo']}\n"
               f"✅ *Dato de memoria (Sin gasto de API)*")
    bot.reply_to(message, resumen, parse_mode="Markdown")

# --- REPORTES Y ALERTAS ---
def enviar_reporte_periodico():
    global conteo_reporte
    reporte = (f"📊 **REPORTE AUTOMÁTICO**\n\n"
               f"📈 Sobrecompras (Toros 🐂): {conteo_reporte['compras']}\n"
               f"📉 Sobreventas (Osos 🐻): {conteo_reporte['ventas']}\n\n"
               f"🔄 *Contadores reiniciados.*")
    bot.send_message(CHAT_ID, reporte, parse_mode="Markdown")
    conteo_reporte = {"compras": 0, "ventas": 0}

def ciclo_centinela():
    global conteo_reporte
    while True:
        rsi_k, precio = obtener_datos_eth()
        if rsi_k is not None:
            if rsi_k <= 20:
                conteo_reporte["ventas"] += 1
                with open('toro.jpg', 'rb') as photo:
                    bot.send_photo(CHAT_ID, photo, caption=f"🔴 **SOBRE VENTA** (Oso 🐻)\n🪙 ETH/USDT\n🎯 Precio: {precio}\n🧑‍💻 RSI: {rsi_k:.2f}")
            elif rsi_k >= 80:
                conteo_reporte["compras"] += 1
                with open('oso.jpg', 'rb') as photo:
                    bot.send_photo(CHAT_ID, photo, caption=f"🟢 **SOBRE COMPRA** (Toro 🐂)\n🪙 ETH/USDT\n🎯 Precio: {precio}\n🧑‍💻 RSI: {rsi_k:.2f}")
        time.sleep(60)

def run_scheduler():
    schedule.every().day.at("12:00").do(enviar_reporte_periodico)
    schedule.every().day.at("21:00").do(enviar_reporte_periodico)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=ciclo_centinela, daemon=True).start()
    bot.polling(none_stop=True)
    
