import LIS2HH12 as Accel
import SI7006A20 as TempHum
import MPL3115A2 as Barometer
from pysense import Pysense
import time
from network import WLAN
import pycom as pyc
import machine

pyc.heartbeat(False)

wlan = WLAN(mode=WLAN.STA)

pyc.rgbled(0xFF0000)
nets = wlan.scan()
for net in nets:
    if net.ssid == 'SDU-VISITOR':
        print('Network found!')
        wlan.connect(net.ssid, auth=None, timeout=5000)
        while not wlan.isconnected():
            machine.idle() # save power while waiting
        print('WLAN connection succeeded!')
        break

if not wlan.isconnected():
    while True:
        pyc.rgbled(0x000000)
        time.sleep(1)
        pyc.rgbled(0xFF0000)
        time.sleep(1)

pyc.rgbled(0x0000FF)
pysen = Pysense()
