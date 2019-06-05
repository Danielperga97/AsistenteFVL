# coding=utf-8
buttons = [10,11,12]
import subprocess 
import RPi.GPIO as GPIO 
import datetime
import os
import time
from serial import Serial
import board 
import neopixel 
import csv

GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
MAX_RECORD_TIME = "10"


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

state =''
pixel = neopixel.NeoPixel(board.D18, 6)
#definiting colours
green = (255,0,0)
red = (0,255,0)
blue = (0,0,255)
violet = (0,201,255)
orange = (70,255,0)
ambar = (255,255,0)
white = (255,255,255)
off = (0,0,0)

def change_color(color):
    for i in range(6):
        time.sleep(0.05)
        pixel[i] = color

def itsTimeExam():
    cout=0
    while(cout<3):
        pixel.fill(white)
        time.sleep(1)
        pixel.fill(off)
        time.sleep(1)
        cout = cout + 1

def powerOff():
    pixel.fill(off)

def transmision():
    arduino = Serial('/dev/ttyACM0', baudrate=9600)
    val = arduino.readline()
    value = int(val.decode("utf-8"))
    return value

def color_confirm(color):
    if(GPIO.input(4) == GPIO.HIGH):
        pixel.fill(off)
        time.sleep(0.2)
        pixel.fill(color)
        time.sleep(0.2)
        pixel.fill(off)
        time.sleep(0.2)
        pixel.fill(color)
        time.sleep(0.2)
        pixel.fill(off)
        time.sleep(0.2)
        pixel.fill(color)
def get_emotion():
    while True:
        data = transmision()
        print(data)
        if(data>=0 and data<=16):
            change_color(red)
            state = 'molesto'
            print(state)
            if(GPIO.input(4) == GPIO.HIGH):
                color_confirm(red)
                break

        elif(data>16 and data<=33):
            change_color(orange)
            state = 'nervioso'
            print(state)
            if(GPIO.input(4) == GPIO.HIGH):
                color_confirm(orange)
                break

        elif(data>33 and data<=50):
            change_color(ambar)
            state = 'triste'
            print(state)
            if(GPIO.input(4) == GPIO.HIGH):
                color_confirm(ambar)
                break

        elif(data>50 and data<=67):
            change_color(green)
            state = 'calmado'
            print(state)
            if(GPIO.input(4) == GPIO.HIGH):
                color_confirm(green)
                break

        elif(data>67 and data<=84):
            change_color(blue)
            state = 'feliz'
            print(state)
            if(GPIO.input(4) == GPIO.HIGH):
                color_confirm(blue)
                break
        elif(data>84 and data<=100):
            change_color(violet)
            state = 'emocionado'
            print(state)
            if(GPIO.input(4) == GPIO.HIGH):
                color_confirm(violet)
                break

    print("Su estado actual es: ",state)
    return state

def filename():
    now = datetime.datetime.now()
    formattedDate = now.strftime("%d_%m_%Y-%H_%M_%S")
    return formattedDate+"-record.wav"

def record(max_record,filename ):
    file= "/media/pi/PACIENTE/audios/"+filename
    print(filename + " will be recorded")
    out = subprocess.Popen([ 'arecord', '-D', 'plughw:1,0', '-f' , 'cd', '-d', max_record , file])
    print(filename+ " was recorded")

    return filename

def playAudio(audioPath):
    out = subprocess.run(['aplay',audioPath])
    return out

def getEmotion():
    return "emotion"

def selectSaludo():
    currentTime = datetime.datetime.now()
    hour=currentTime.hour
    audio="/home/pi/AssistantFVL/Voice_User_Interface/1.3-Buenos_días.wav"
    if hour>12 and hour<=18:
        audio="/home/pi/AssistantFVL/Voice_User_Interface/1.2-Buenas_tardes.wav"
    elif hour >18:
        audio="/home/pi/AssistantFVL/Voice_User_Interface/1.1-Buenas_noches.wav"
    else:
        audio="/home/pi/AssistantFVL/Voice_User_Interface/1.3-Buenos_días.wav"
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
    if datetime.datetime.now() < start+datetime.timedelta(days=8):
        day4=True
    return day4

def generateLabel(message,icon):
    os.system("sudo python3 /home/pi/AssistantFVL/dymo-labelgen/main.py --font_size 8 --output /home/pi/AssistantFVL/label.pdf --icon /home/pi/AssistantFVL/dymo-labelgen/icons/"+icon+".png " + message)

def printLabel():
    os.system("lpr -P DYMO_LabelWriter_450_Turbo /home/pi/AssistantFVL/label.pdf" )

def generateMessage(emotion):
    ft=open("/home/pi/AssistantFVL/tmp.txt","w")
    with open("/home/pi/AssistantFVL/Consejos_Semana_1/"+emotion+".txt","r") as fp:
        lines= fp.readlines()
        cnt=0
        phrase=lines[cnt]
        for line in lines:
            if not line.startswith("#"):
                phrase=line
                lines[cnt]="#"+phrase
                break
        cnt+=1
    ft.writelines(lines)
    fp.close()
    ft.close()
    os.system("sudo rm -rf /home/pi/AssistantFVL/Consejos_Semana_1/"+emotion+".txt")
    os.system("sudo mv /home/pi/AssistantFVL/tmp.txt /home/pi/AssistantFVL/Consejos_Semana_1/"+emotion+".txt")
    os.system("sudo chmod 777 /home/pi/AssistantFVL/Consejos_Semana_1/"+emotion+".txt")
    return phrase

def writeResult(emotion):
    t = datetime.datetime.now()
    ft = t.strftime("%d/%m/%Y-%H:%M:%S")
    row=[ emotion,ft]
    with open('/media/pi/PACIENTE/results.csv', 'a+') as csvFile:
        writer = csv.writer(csvFile,delimiter=';')
        writer.writerow(row)
    csvFile.close()

if __name__ == "__main__":
    itsTimeExam()
    saludo=selectSaludo()
    playAudio(saludo)
    print(saludo)
    day4=instructions()
    recordname=""
    if day4:
        playAudio("/home/pi/AssistantFVL/Voice_User_Interface/2-nstruccionesPrompt1.wav")
    #emocion=girarRuleta()
        #PASO 1, RULETA
    emotion=get_emotion()
    print(emotion)
    playAudio("/home/pi/AssistantFVL/Voice_User_Interface/3-Porquetesientesasi.wav")
    if day4:
        playAudio("/home/pi/AssistantFVL/Voice_User_Interface/4-InstruccionesPrompt2.wav")
    while True:
        #pASO2, GRABACION
        if GPIO.input(17) == GPIO.HIGH:
            print("Button 2 was pushed!")
            time.sleep(0.5)
            recordname=filename()
            record("60",recordname)
            break
    while True:
        if GPIO.input(17) == GPIO.LOW:
            print("Button 2 was released!")
            stop_recording()
            time.sleep(1)
            playAudio("/media/pi/PACIENTE/audios/"+recordname)
            break
    playAudio("/home/pi/AssistantFVL/Voice_User_Interface/5-Confirmargrabacion.wav")
    while True:
    #pASO2, GRABACION se repite
        if GPIO.input(17) == GPIO.HIGH:
            print("Button 2 was pushed!")
            recordname=filename()
            record("60",recordname)
            while True:
                if GPIO.input(17) == GPIO.LOW:
                    print("Button 2 was released!")
                    stop_recording()
                    time.sleep(1)
                    playAudio("/media/pi/PACIENTE/audios/"+recordname)
                    break
            playAudio("/home/pi/AssistantFVL/Voice_User_Interface/5-Confirmargrabacion.wav")
        if GPIO.input(27) == GPIO.HIGH:
            print("Grabacion confirmada!")
            message=generateMessage(emotion)
            phrase = '"{}"'.format(message)
            print(phrase)
            generateLabel(phrase,emotion)
            printLabel()
            writeResult(emotion)
            playAudio("/home/pi/AssistantFVL/Voice_User_Interface/6-Tomaremocion.wav")
            playAudio("/home/pi/AssistantFVL/Voice_User_Interface/7.1-Cierreenunashoras.wav")
            powerOff()
            break
