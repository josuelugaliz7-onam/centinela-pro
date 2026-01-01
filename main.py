import telebot
import time

# Datos de Telegram proporcionados
TOKEN = '8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0'
CHAT_ID = '7951954749'

def iniciar_bot():
    try:
        # Inicializamos el bot con el token corregido
        bot = telebot.TeleBot(TOKEN)
        
        # Mensaje de confirmación de encendido
        mensaje = "🚀 ¡Onam! El Centinela ya está VIVO y conectado correctamente a tu Telegram."
        bot.send_message(CHAT_ID, mensaje)
        
        print("✅ Mensaje enviado con éxito. El bot está funcionando.")
        
        # Bucle para mantener el proceso activo en Render
        while True:
            time.sleep(60)
            
    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")

if __name__ == "__main__":
    iniciar_bot()
    
