#Codigo para el bot de telgram Guarning
import os
from gpiozero import LED
import telebot
from datetime import datetime
from CotrolProyecto import ControlProyecto

bot=telebot.Telebot("5198248925:AAHSnTII8zvxnV7yA76RQziHT0DFNdGsGmw",parse_mode=None)
#Función que muestra el dia por telegram  
def BotGuarning(): 
    @bot.message_handler(commands=['/dia'])
    def send_welcome(message):
        dia = datetime.today().strftime('%A, %B %d, %Y %H:%M:%S') #Se trata de la obtencion del dia con su formato
        bot.reply_to(message, dia)

    #Función que regresa el numero de vasos que se han servido en total por telegram
    @bot.message_handler(commands=['/totales'])
    def send_welcome(message, contador_vasos):
        bot.reply_to(message,"Se han servido"+ contador_vasos +"vasos :)")

    #Función que regresa el estado de la bomba por telegram
    @bot.message_handler(commands=['status'])
    def send_welcome(message, estado):
        bot.reply_to(message, estado)

    @bot.message_handler(func=lambda message:true)
    def echo_all(message):
        bot.reply_to(message,message.txt)


bot.infinity_polling()