from pysense import Pysense
import time
from network import WLAN
import network
import pycom as pyc
import machine
import socket
from _thread import start_new_thread

def log(s):
    print(s)



AP_SSID = 'Hest123'
AP_AUTH = (network.WLAN.WPA2, 'wwoo2206')

AP_TIMEOUT = 5000
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
    while True:
        pyc.rgbled(0x000000)
        time.sleep(0.5)
        pyc.rgbled(0xFFFFFF)
        time.sleep(0.5)

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

hostSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#host = socket.socket() #socket.gethostbyname(socket.gethostname())
connected_ip = wlan.ifconfig()[0]
log(connected_ip)
hostSocket.bind((connected_ip, HOST_PORT))
hostSocket.listen()
log("Parcel x started on " + connected_ip + " port " + str(HOST_PORT))
start_new_thread(client_socket_accept_loop, ())

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
