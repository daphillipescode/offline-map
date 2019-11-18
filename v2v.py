import RPi.GPIO as GPIO
import time
import lcddriver
import pynmea2
import string
import spidev
import serial
import select
import socket
from numpy import interp


#CAR 2 -- SERVER
CAR_2_IP = "192.168.43.132"
CAR_2_PORT = 5006

#CLIENTS
CAR_1_IP = "192.168.43.131"
CAR_1_PORT = 5005
CAR_3_IP = "192.168.43.133"
CAR_3_PORT = 5007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((CAR_2_IP, CAR_2_PORT))

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
buzzer = 27
led = 22

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6,  GPIO.IN,  pull_up_down=GPIO.PUD_UP)
GPIO.setup(5,  GPIO.IN,  pull_up_down=GPIO.PUD_UP)
GPIO.setup(buzzer,  GPIO.OUT)
GPIO.setup(led,  GPIO.OUT)

display = lcddriver.lcd()
spi = spidev.SpiDev()
spi.open(0,0)
gps = ''
connection = "CONNECTION"

def analogInput(channel):
    spi.max_speed_hz = 100
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def coordinates():
    global gps
    port="/dev/ttyAMA0"
    ser=serial.Serial(port, baudrate=9600, timeout=0.1)
    dataout = pynmea2.NMEAStreamReader()
    newdata=ser.readline()

    if newdata[0:6] == "$GPRMC":
        newmsg=pynmea2.parse(newdata)
        lat=newmsg.latitude
        lng=newmsg.longitude
        val = "LAT : " + str(lat) + ",LONG: " + str(lng)
        gps = str(val)
        return gps

def sendOvertakeText(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def sendYesText(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)
    
def sendNoText(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def sendLeft(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def sendRight(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def sendRequest(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def sendResponse(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def sendRequest(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)


def overspeeding(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def detect(msg):
    sock.sendto(msg, (CAR_1_IP, CAR_1_PORT))
    sock.sendto(msg, (CAR_3_IP, CAR_3_PORT))
    time.sleep(0.2)

def buzzerTrigger():
    GPIO.output(buzzer, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(buzzer, GPIO.LOW)
    time.sleep(0.1)

def ledLight():
    GPIO.output(led, GPIO.HIGH)


while True:
    btn1 = GPIO.input(21)
    btn2 = GPIO.input(20)
    btn3 = GPIO.input(16)
    btn4 = GPIO.input(13)
    btn5 = GPIO.input(6)
    btn6 = GPIO.input(5)

    output = analogInput(0)
    speed = int(interp(output, [0, 1023], [0, 100]))
    
    detect(connection)
    coordinates()

    msg2 = 'SPEED:,'+ str(speed).encode('utf-8')
    #msg3 = gps
    msg3 = "LAT : 8.2222,LONG: 125.2222"
    try:
        ready_to_read, ready_to_write, in_error = \
            select.select([sock,],[sock,],[],5)
    except select.error:
        sock.shutdown(2)
        sock.close()
        print("Connection Error")
        break
    if len(ready_to_read) == 0:
        GPIO.output(led, GPIO.LOW)
        print("LOW")

    if len(ready_to_read) > 0:
        data, addr = sock.recvfrom(1024)
        msg = data.decode('utf-8')
        
        if msg == 'REQUEST':
            msg1 = 'XKM 2222:,Speed&Location'.encode('utf-8')
            msg2 = 'SPEED:,'+ str(speed).encode('utf-8')
            messages = [msg1, msg2, msg3]
            for x in range(3):
                msg = str(messages[x])
                sendResponse(msg)
        elif msg == 'CONNECTION':
            ledLight()
        else:
            newMsg = msg.split(",")
            print(str(newMsg[0]))
            print(str(newMsg[1]))
            display.lcd_display_string(str(newMsg[0]), 1)
            display.lcd_display_string(str(newMsg[1]), 2)
            for i in range(5):
                buzzerTrigger()
            time.sleep(2)
            display.lcd_clear()
        


    #MESSAGING AREA
    if len(ready_to_write) > 0:
        if speed >= 65:
            msg1 = 'WARNING!:, OVERSPEEDING!!?'.encode('utf-8')
            messages = [msg1, msg2, msg3]
            for x in range(3):
                msg = str(messages[x])
                overspeeding(msg)

        if btn1 == False:
            print('BTN 1')
            msg1 = 'XKM 2222:,Can I Overtake?'.encode('utf-8')
            messages = [msg1, msg2, msg3]
            for x in range(3):
                msg = str(messages[x])
                print(msg)
                sendOvertakeText(msg)

        if btn2 == False:
            print('BTN 2')
            msg1 = 'XKM 2222:,Yes!'.encode('utf-8')
            messages = [msg1, msg2, msg3]
            for x in range(3):
                msg = str(messages[x])
                print(msg)
                sendYesText(msg)

        if btn3 == False:
            print('BTN 3')
            msg1 = 'XKM 2222:,No!'.encode('utf-8')
            messages = [msg1, msg2, msg3]
            for x in range(3):
                msg = str(messages[x])
                print(msg)
                sendNoText(msg)

        if btn4 == False:
            print('BTN 4')
            msg1 = 'XKM 2222:,Turning Left!'.encode('utf-8')
            messages = [msg1, msg2, msg3]
            for x in range(3):
                msg = str(messages[x])
                print(msg)
                sendLeft(msg)

        if btn5 == False:
            print('BTN 5')
            msg1 = 'XKM 2222:,Turning Right!'.encode('utf-8')
            messages = [msg1, msg2, msg3]
            for x in range(3):
                msg = str(messages[x])
                print(msg)
                sendRight(msg)

        if btn6 == False:
            print('BTN 6')
            msg = 'REQUEST'.encode('utf-8')
            msg = str(messages)
            sendRequest(msg)