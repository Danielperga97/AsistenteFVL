# coding=utf-8
buttons = [10,11,12]
import subprocess 
import RPi.GPIO as GPIO 
import datetime
import os
import time

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BOARD)

GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

MAX_RECORD_TIME = "10"
def filename():
    now = datetime.datetime.now()
    formattedDate = now.strftime("%d_%m_%Y-%H_%M_%S")
    return formattedDate+"-record.wav"

def record(max_record,filename ):
    print(filename + " will be recorded")
    out = subprocess.Popen(['sudo', 'arecord', '-D', 'plughw:1,0', '-f' , 'cd', '-d', max_record , filename])
    print(filename+ " was recorded")

    return filename

def playAudio(audioPath):
    out = subprocess.call(['sudo','aplay',audioPath])
    return out

def getEmotion():
    return "emotion"

def selectSaludo():
    currentTime = datetime.datetime.now()
    hour=currentTime.hour
    audio="Voice_User_Interface/1.3-Buenos_días.wav"
    if hour>12 and hour<=18:
        audio="Voice_User_Interface/1.2-Buenas_tardes.wav"
    elif hour >18:
        audio="Voice_User_Interface/1.1-Buenas_noches.wav"
    else:
        audio="Voice_User_Interface/1.3-Buenos_días.wav"
    return audio

def stop_recording():
    subprocess.call(["pkill","-9", "arecord"])
def instructions():
    exists = os.path.isfile('/home/pi/AssistantFVL/register.txt')
    start="datetime.datetime.now()"
    day4=False
    if exists:
        f=open('/home/pi/AssistantFVL/register.txt')
        first_line = f.readline()
        start = datetime.datetime.strptime(first_line, '%d_%m_%Y-%H_%M_%S') 
        # Store configuration file values
    else:
        start= datetime.datetime.now()
        f= open("/home/pi/AssistantFVL/register.txt","w+")
        f.write(start.strftime("%d_%m_%Y-%H_%M_%S"))
    if datetime.datetime.now() < start+datetime.timedelta(days=4):
        day4=True
    return day4

def generateLabel(message):
    os.system("sudo python3 /home/pi/AssistantFVL/dymo-labelgen/main.py --font_size 12 " + message)

def printLabel():
    os.system("lpr -P DYMO_LabelWriter_450_Turbo /home/pi/AssistantFVL/label.pdf" )

if __name__ == "__main__":
    saludo=selectSaludo()
    playAudio(saludo)
    print(saludo)
    day4=instructions()
    recordname=""
    if day4:
        playAudio("Voice_User_Interface/2-nstruccionesPrompt1.wav")
    #emocion=girarRuleta()
    while True:
        #PASO 1, RULETA
        if GPIO.input(10) == GPIO.HIGH:
            print("Emocion Confirmada")
            break
    playAudio("Voice_User_Interface/3-Porquetesientesasi.wav")
    if day4:
        playAudio("Voice_User_Interface/4-InstruccionesPrompt2.wav")
    while True:
        #pASO2, GRABACION
        if GPIO.input(11) == GPIO.HIGH:
            print("Button 2 was pushed!")
            recordname=filename()
            record("60",recordname)
            break
    while True:
        if GPIO.input(11) == GPIO.LOW:
            print("Button 2 was released!")
            stop_recording()
            time.sleep(1)
            playAudio(recordname)
            break
    playAudio("Voice_User_Interface/5-Confirmargrabacion.wav")
    while True:
        if GPIO.input(12) == GPIO.HIGH:
            print("Grabacion confirmada!")
            message="mensaje de prueba"
            phrase = '"{}"'.format(message)
            generateLabel(phrase)
            printLabel()
            playAudio("Voice_User_Interface/6-Tomaremocion.wav")
            playAudio("Voice_User_Interface/7.1-Cierreenunashoras.wav")
            break
