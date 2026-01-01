import telebot
import time
import requests
import pandas as pd
import threading 

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
                
                # RSI Simple
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

# --- TU COMANDO PERSONALIZADO ---
@bot.message_handler(commands=['status', 'hola'])
def enviar_status(message):
    bot.reply_to(message, "¡ACTIVO JEFE 😎 estoy Vivo y Patrullando!")

if __name__ == "__main__":
    threading.Thread(target=analizar_mercado, daemon=True).start()
    bot.send_message(CHAT_ID, "🚀 Sistema actualizado, Jefe. Escriba /status para ver mi estado.")
    bot.polling(none_stop=True)
    
