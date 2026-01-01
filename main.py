import telebot

# Pega tu token EXACTO aquí. Debe verse algo como '123456:ABC-DEF...'
TOKEN = '8169583738:AAGzzzFkPRLqE_33M-knJol9HMD6vHP_Rx0' 
CHAT_ID = '7951954749'

def iniciar_centinela():
    try:
        bot = telebot.TeleBot(TOKEN)
        bot.send_message(CHAT_ID, "🚀 ¡Onam! El Centinela está VIVO. La conexión es correcta.")
        print("✅ Conexión exitosa con Telegram")
    except Exception as e:
        print(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    iniciar_centinela()
    
