from pysense import Pysense
import time
from network import WLAN
import network
import pycom as pyc
import machine
import time
import urequests as requests
import ujson
import socket
from _thread import start_new_thread

def log(s):
    print(s)

REMOTE_SERVER_IP = '193.183.99.180'
AP_SSID = 'SDU-VISITOR' #'Pixel'
AP_AUTH = None #(network.WLAN.WPA2, '17863860b3f7')
ALARM_STATE = False
DEVICE_ID = '1' #set id
AP_TIMEOUT = 5000
GEOLOCATION_KEY = 'AIzaSyAp4CFGfNl1psTfOvK9rp9PuilvIAdIJUE'
HOST_PORT = 6002

pyc.heartbeat(False)

wlan = WLAN(mode=WLAN.STA)
pyc.rgbled(0xFF0000)

nets = wlan.scan()
for net in nets:
    if net.ssid == AP_SSID:
        log('Network found!')
        wlan.connect(net.ssid, auth=AP_AUTH, timeout=AP_TIMEOUT)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        log('WLAN connection succeeded!')
        break


if not wlan.isconnected():
    while True:
        pyc.rgbled(0x000000)
        time.sleep(1)
        pyc.rgbled(0xFF0000)
        time.sleep(1)

pyc.rgbled(0x0000FF)
pysen = Pysense()

def sensorFailedLoop():
    while True:
        pyc.rgbled(0x000000)
        time.sleep(1)
        pyc.rgbled(0x0000FF)
        time.sleep(1)

def activateBlinkAlarm():
    ALARM_STATE = True
    for x in range(1, 10): #10 cycles
        pyc.rgbled(0x000000)
        time.sleep(0.5)
        pyc.rgbled(0xFFFFFF)
        time.sleep(0.5)
    ALARM_STATE = False

def setNormalLEDState():
    pyc.rgbled(0x00FF00)

def client_recieve_loop(clientSocket,clientAddress):
    print("Accepted connection from " + str(clientAddress))
    while True:
        clientMessage = clientSocket.recv(1024)
        if not clientMessage: break
        if(str(clientMessage) == 'alarm'):
            activateBlinkAlarm()
        log("Message from client: " + str(clientMessage))
    clientSocket.close()

def client_socket_accept_loop():
    while True:
        clientSocket, clientAddress = hostSocket.accept()
        start_new_thread(client_recieve_loop,(clientSocket,clientAddress))

def client_poll_alarmStatus_loop(): #method is blocking, execute in a seperate thread
    while True:
        response = requests.get('http://' + REMOTE_SERVER_IP +'/alarm?id=' + DEVICE_ID)
        log('Response from server: ' + str(response))
        if response == 'True':
            activateBlinkAlarm()
        else:
            time.sleep(5)

#hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connected_ip = wlan.ifconfig()[0]
#log(connected_ip)
#hostSocket.bind((connected_ip, HOST_PORT))
#hostSocket.listen()
#log("Parcel x started on " + connected_ip + " port " + str(HOST_PORT))

start_new_thread(client_poll_alarmStatus_loop, ())

log("Checking for sensors")

log("Checking accelerometer")
from LIS2HH12 import LIS2HH12
accel = LIS2HH12(pysen)
if accel.acceleration() == None or accel.acceleration() == (None, None, None):
    log("No accelerometer availale")
    sensorFailedLoop()
log("Accelerometer is available")
log("Checking temperature and humidity sensor")
from SI7006A20 import SI7006A20
tempSens = SI7006A20(pysen)
if tempSens.humidity() == None or tempSens.temperature() == None:
    log("No temperature or humidity sensor available")
    sensorFailedLoop()
log("Temperature and humidity is available")
log("Checking barometer")
from MPL3115A2 import MPL3115A2
barometer = MPL3115A2(pysen)
if barometer.pressure() == None:
    log("No barometer available")
    sensorFailedLoop()
log("Barometer is available")

pyc.rgbled(0x00FF00)

def estimateLocation():
    url = "http://193.183.99.180/geolocation"
    data = {"homeMobileCountryCode": 238,"homeMobileNetworkCode": 10,"radioType": "lte",
    "carrier": "TDC Denmark",
      "considerIp": "true",
      "cellTowers": [],
      "wifiAccessPoints": []
    }

    nets = wlan.scan()
    accessPoints = []
    import struct
    for net in nets:
        accessPoints.append({"macAddress":"%x:%x:%x:%x:%x:%x" % struct.unpack("BBBBBB",net.bssid), "signalStrength":net.rssi, "age":net.sec*1000, "channel": net.channel})

    data["wifiAccessPoints"] = accessPoints
    print(data)

    r = requests.post(url, json=data)
    print(r.status_code)
    return r.json()

def calculateAccelData(data):
    import math
    calculatedData = []
    for i in range(len(data)):
        index = math.floor(i / 10)
        if i % 10 == 0:
            calculatedData.append((abs(data[i][0]), abs(data[i][1]), abs(data[i][2])))
        else:
            calculatedData[index] = (calculatedData[index][0] + abs(data[i][0]), calculatedData[index][1] + abs(data[i][1]), calculatedData[index][2] + abs(data[i][2]))
    return calculatedData

accelData = []
tempData = []
humData = []
baroData = []
gpsData = []

import utime
iterations = 1
while True:
    startTime = utime.ticks_ms()

    res = accel.acceleration()
    accelData.append(res)

    if iterations % 10 == 0:
        pyc.rgbled(0x00FF00)
        tempData.append(tempSens.temperature())
        humData.append(tempSens.humidity())
        baroData.append(barometer.pressure())
        gpsData.append(estimateLocation())

    if (iterations-1) % 10 == 0:
        pyc.rgbled(0x000000)

    if iterations == 60:
        calculatedAccelData = calculateAccelData(accelData)
        isExtreme = False

        for i in calculatedAccelData:
            if i[0] > 20 or i[1] > 20 or i[2] > 20:
                isExtreme = True
        for i in tempData:
            if i > 55 or i < -40:
                isExtreme = True
        for i in humData:
            if i > 90:
                isExtreme = True
        for i in baroData:
            if i > 150000 or i < 10000:
                isExtreme = True

        #SEND DATA (ASYNC)

        accelData = []
        tempData = []
        humData = []
        baroData = []
        gpsData = []
        iterations = 1

    iterations += 1
    endTime = utime.ticks_ms()
    time.sleep(1 - (endTime-startTime)/1000)
