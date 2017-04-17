#!/usr/bin/python3
# coding=utf-8
"""reads barometric pressure sensor and writes it to UDP socket with timestamp
"""
import socket
from datetime import datetime
from time import sleep
from time import time

import ms5637

__author__ = 'Moe'
__copyright__ = 'Copyright 2017  Moe'
__license__ = 'MIT'
__version__ = '0.0.2'

# Bari sensor of MS5637
sensor = ms5637.Chip()
bari_file = 'bari_data.csv'


UDP_IP = "192.168.0.2"  # Big Machine
UDP_PORT = 6421  # bARI port
MESSAGE = "Get ready to rumble."

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print("message:", MESSAGE)

while True:
    try:
        now = time()
        humantime = datetime.fromtimestamp(now).strftime('%Y-%m-%dT%H:%M:%S')
        pressure, _temperature = sensor.get_data()

    except OSError:
        sensor.__init__()
        pressure, temperatue = sensor.get_data()

    finally:
        outstring = str(humantime) + ', ' + str(pressure)
        outstring = outstring.encode()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(outstring, (UDP_IP, UDP_PORT))

        sleep(1)
