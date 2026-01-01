import telebot
import time
import requests
import pandas as pd

# Datos de Onam
TOKEN = '8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0'
CHAT_ID = '7951954749'
bot = telebot.TeleBot(TOKEN)

# Configuración de Monedas y URLs de imágenes
MONEDAS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'RNDRUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT', 'NEARUSDT']
IMG_TORO = 'https://raw.githubusercontent.com/OnamTrader/Bot/main/toro.jpg' # Asegúrate de que el nombre coincida en tu GitHub
IMG_OSO = 'https://raw.githubusercontent.com/OnamTrader/Bot/main/oso.jpg'

def obtener_datos(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'close_time', 'q_vol', 'trades', 'tb_base', 'tb_quote', 'ignore'])
    return df['close'].astype(float)

def calcular_rsi_stoch(series, period=14):
    # Lógica simplificada de RSI Stoch para el bot
    rsi = series.diff().apply(lambda x: x if x > 0 else 0).rolling(period).mean() / series.diff().apply(lambda x: abs(x)).rolling(period).mean()
    stoch_rsi = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    return stoch_rsi * 100

def ejecutar_centinela():
    while True:
        for moneda in MONEDAS:
            try:
                precios = obtener_datos(moneda)
                valor_rsi = calcular_rsi_stoch(precios).iloc[-1]
                precio_actual = precios.iloc[-1]
                
                # SEÑAL DE COMPRA (Sobreventa)
                if valor_rsi < 20:
                    tp = precio_actual * 1.005 # +0.5%
                    sl = precio_actual * 0.995 # -0.5%
                    msg = f"🟢 **COMPRA: {moneda}**\n\nNivel RSI: {valor_rsi:.2f}\nPrecio: ${precio_actual}\n✅ TP: ${tp:.2f}\n❌ SL: ${sl:.2f}"
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg, parse_mode='Markdown')
                
                # SEÑAL DE VENTA (Sobrecompra)
                elif valor_rsi > 80:
                    tp = precio_actual * 0.995
                    sl = precio_actual * 1.005
                    msg = f"🔴 **VENTA: {moneda}**\n\nNivel RSI: {valor_rsi:.2f}\nPrecio: ${precio_actual}\n✅ TP: ${tp:.2f}\n❌ SL: ${sl:.2f}"
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg, parse_mode='Markdown')
                
            except Exception as e:
                print(f"Error con {moneda}: {e}")
        
        time.sleep(900) # Revisa cada 15 minutos (mismo tiempo que tus velas)

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "🚀 Estrategia Multi-Moneda Iniciada. Vigilando 10 activos...")
    ejecutar_centinela()
                    
