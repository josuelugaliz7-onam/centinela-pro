# ... (mantén tus importaciones y configuraciones igual)

def analizar_mercado():
    global stats
    print("SISTEMA DE ESCANEO INICIADO 🚀") # Esto aparecerá en los logs
    bot.send_message(CHAT_ID, "🔎 El Centinela ha comenzado a patrullar las 10 monedas...")
    
    while True:
        for moneda in MONEDAS:
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={moneda}&interval=15m&limit=100"
                res = requests.get(url)
                data = res.json()
                
                k, d = calcular_stoch_rsi(data)
                # Bajamos un poco la exigencia para la prueba: 25 y 75
                if k < 25: 
                    msg = f"🟢 **TORO DETECTADO en {moneda}**\nStoch RSI: {k:.2f}"
                    bot.send_photo(CHAT_ID, IMG_TORO, caption=msg)
                    stats["compras"] += 1
                    time.sleep(5)
                elif k > 75:
                    msg = f"🔴 **OSO DETECTADO en {moneda}**\nStoch RSI: {k:.2f}"
                    bot.send_photo(CHAT_ID, IMG_OSO, caption=msg)
                    stats["ventas"] += 1
                    time.sleep(5)
            except Exception as e:
                print(f"Error en {moneda}: {e}")
        time.sleep(60)
        
