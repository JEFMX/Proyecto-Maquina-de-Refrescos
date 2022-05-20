from ossaudiodev import control_labels
from signal import pause
from gpiozero import DistanceSensor
from signal import pause
from bluedot import BlueDot
from EchoBot import BotGuarning
import RPi.GPIO as GPIO
import time
import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from gpiozero import LED
import subprocess

contador_vasos = 0 #Variable donde se guardan el numero total de vasos

#Función encargada de gestionar todo el funcionamiento de la maquina de refrescos
def ControlProyecto(contador_vasos):
    servoPIN =26 #Pin de control para el servo
    #Configuración incial del servo
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(servoPIN, GPIO.OUT)
    p2 = GPIO.PWM(servoPIN, 50) 
    p2.start(12) 

    #Objeto para controlar el bluedot
    bd=BlueDot()

    #PARA LEDS pines
    #led de ultrasonico cuando esta en espera
    led_rojo=LED(10)
    #led del  servo 
    led_verdeS=LED(22)
    #led del ultrasonico cuando funciona
    led_verdeU=LED(9)
    #Configuración inicial del motor
    ini=23
    ena=24
    #PARA sensor pines
    trig=17
    echo=18
    #Configuración inicial de sensor y motor
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ini,GPIO.OUT)
    GPIO.setup(ena,GPIO.OUT)
    GPIO.setup(trig,GPIO.OUT)
    GPIO.setup(echo,GPIO.IN)
    p=GPIO.PWM(ena,1000)
    p.start(25)
    
    #------------------------------------------para el oled
    # Define el reseteo del pin
    oled_reset = digitalio.DigitalInOut(board.D4)
    #Función con la logia de operacion del servo destinado a la apertura del deposito de hielos
    def dpad(pos):
        if pos.top:
            p2.ChangeDutyCycle(1) #Valor que abre el servo 0 grados equivale
            time.sleep(0.5) #Espera de medio segundo
            print("abierto")
            led_verdeS.on() #Enciende el led verde
        elif pos.bottom:
            p2.ChangeDutyCycle(12) #Valor que cierra el servo 180 grados equivale
            time.sleep(0.5) #Espera de medio segundo
            print("cerrado")  
            led_verdeS.off() #Apaga el led verde

    # Parametros del display
    WIDTH = 128
    HEIGHT = 64
    BORDER = 5

    # Protocolo IC2 para la comunicación con el OLED
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

    # Limpiar el display
    oled.fill(0)
    oled.show()

    # Crea un espacio de dibujado
    # Establece el color y los parametros de la ventana en el oled
    image = Image.new("1", (oled.width, oled.height))

    # Se obtiene el obejeto de dibujo apra dibujar sobre el Panel
    draw = ImageDraw.Draw(image)

    # Dibuja un fondo
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
    #Establece la fuente
    font = ImageFont.truetype('PixelOperator.ttf', 16)


    #Espera que se aprieta el boton de bluedot para el manejo del servo
    bd.when_pressed = dpad

    #Cacha todas las excepciones que peudan producirse y altera el funcionamiento
    try:
        while True:
            #--ACCION OLED
            #--ACCION SENSOR
            GPIO.output(trig,GPIO.LOW)
            time.sleep(0.5)

            GPIO.output(trig,GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(trig,GPIO.LOW)

            #Mantien la escucha del sensor
            while True:
                pulso_inicio=time.time()
                if(GPIO.input(echo)==GPIO.HIGH):
                    break
            
            #Dispara la señal ultrasonica
            while True:
                pulso_fin=time.time()
                if(GPIO.input(echo)==GPIO.LOW):
                    break 
            #Calculos para la distancia del vaso
            duracion=pulso_fin-pulso_inicio
            distancia=34300*duracion/2
            print("Distancia :",distancia)

            #---ACCION MOTOR
            if distancia<7:
                #Leds de estados de operación
                led_verdeU.on()
                led_rojo.off()
                print("sirviendo refresco")  
                estado = 'Sirviendo' #El estado que se envia al bot de telegram
                GPIO.output(ini,GPIO.HIGH)
                # Dibuja el mensaje de que se esta sirviendo algo
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((0, 0), "Sirviendo refresco" , font=font, fill=255)
                # Muestra el mensaje
                oled.image(image)
                oled.show()
                contador_vasos = contador_vasos + 1 #esta es la variable que cuenta el numero de vasos servidos
                time.sleep(.1)
            else:
                #Leds de estados de operación
                led_verdeU.off()
                led_rojo.on()
                print("esperando refresco")
                estado = 'En espera' #El estado que se envia al bot de telegram
                GPIO.output(ini,GPIO.LOW)
                # Dibuja el mensaje de que se ha quitado el vaso (no se sirve nada)
                draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
                draw.text((0, 0), "Quitaste el vaso " , font=font, fill=255)
                #Muestra el mensaje
                oled.image(image)
                oled.show()
                time.sleep(.1)

    except KeyboardInterrupt:
        GPIO.cleanup() #Limpia los procesos que puedan quedarswe atorados en lso pines 
        p.stop() #Para el motor ante cualquier anomalia
    return contador_vasos, estado #Retonar las variables para el bot


#Manda a llamar todo el codigo de control
def main():
    ControlProyecto()
    BotGuarning()