from pysense import Pysense
import time
from network import WLAN
import pycom as pyc
import machine

def log(s):
    print(s)

AP_SSID = 'SDU-VISITOR'
AP_TIMEOUT = 5000

pyc.heartbeat(False)

wlan = WLAN(mode=WLAN.STA)
pyc.rgbled(0xFF0000)
nets = wlan.scan()
for net in nets:
    if net.ssid == AP_SSID:
        log('Network found!')
        wlan.connect(net.ssid, auth=None, timeout=AP_TIMEOUT)
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
