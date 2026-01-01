import telebot
import time

# Datos oficiales de Onam
TOKEN = '8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0'
CHAT_ID = '7951954749'

def iniciar_bot():
    try:
        # Conexión con el Token corregido
        bot = telebot.TeleBot(TOKEN)
        
        # Enviamos el primer mensaje de éxito
        bot.send_message(CHAT_ID, "🚀 ¡Onam! El Centinela ya está VIVO. La conexión con Telegram es perfecta.")
        print("✅ Bot iniciado y mensaje enviado.")

        # Mantenemos el bot encendido
        while True:
            time.sleep(60)
            
    except Exception as e:
        print(f"❌ Error al conectar: {e}")

if __name__ == "__main__":
    iniciar_bot()
    
