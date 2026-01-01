import telebot
import os

# Configura tus credenciales aquí
TOKEN = 'TU_TOKEN_DE_BOTFATHER'
CHAT_ID = 'TU_CHAT_ID_DE_USERINFOBOT'

bot = telebot.TeleBot(TOKEN)

def probar_conexion():
    try:
        mensaje = "🚀 ¡Onam! El Centinela está encendido y listo para el 2026."
        bot.send_message(CHAT_ID, mensaje)
        print("Mensaje enviado con éxito a Telegram")
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

if __name__ == "__main__":
    probar_conexion()
    
