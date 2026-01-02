import os
import time
import telebot
import ccxt
from threading import Thread
from flask import Flask

# --- CONFIGURACIÓN ---
TOKEN = "8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0"
CHAT_ID = "7951954749"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Usamos CCXT para conectar con Binance (Más estable)
exchange = ccxt.binance()
MONEDAS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT"]

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

def patrullaje_automatico():
    print("🚀 PATRULLAJE AUTOMÁTICO INICIADO")
    while True:
        for simbolo in MONEDAS:
            try:
                # Obtenemos velas de 15m
                ohlcv = exchange.fetch_ohlcv(simbolo, timeframe='15m', limit=50)
                cierres = [x[4] for x in ohlcv]
                precio_actual = cierres[-1]
                rsi = calcular_rsi_manual(cierres)

                # ALERTAS AUTOMÁTICAS
                if rsi < 20:
                    msg = f"🟢 **ALERTA TORO: {simbolo}**\n📊 RSI Stoch: {rsi:.2f}\n💰 Precio: ${precio_actual}\n\n¡Zona de rebote detectada!"
                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                elif rsi > 80:
                    msg = f"🔴 **ALERTA OSO: {simbolo}**\n📊 RSI Stoch: {rsi:.2f}\n💰 Precio: ${precio_actual}\n\n¡Zona de venta detectada!"
                    bot.send_message(CHAT_ID, msg, parse_mode="Markdown")
                
                time.sleep(2) # Pausa entre monedas
            except Exception as e:
                print(f"Error en {simbolo}: {e}")
        
        time.sleep(60) # Espera 1 minuto para el siguiente escaneo

@bot.message_handler(commands=['reporte'])
def reporte_manual(message):
    bot.reply_to(message, "🔍 Generando reporte flash...")
    info = "📊 **ESTADO DEL MERCADO**\n"
    for simbolo in MONEDAS:
        try:
            ohlcv = exchange.fetch_ohlcv(simbolo, timeframe='15m', limit=50)
            rsi = calcular_rsi_manual([x[4] for x in ohlcv])
            precio = ohlcv[-1][4]
            info += f"🔹 **{simbolo}**: {rsi:.2f} | ${precio}\n"
        except: info += f"❌ **{simbolo}**: Error\n"
    bot.send_message(message.chat.id, info, parse_mode="Markdown")

@app.route('/')
def home(): return "Bot Activo"

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    Thread(target=patrullaje_automatico).start()
    bot.infinity_polling()
    
