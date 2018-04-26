#!/usr/bin/python3
# coding=utf-8
"""reads barometric pressure sensor and writes it to UDP socket with timestamp available
"""
import socket
from datetime import datetime
from struct import pack
from time import sleep
from time import time
from os import _exit as dumbnrun

import ms5637

__author__ = 'Moe'
__copyright__ = 'Copyright 2017-2018  Moe'
__license__ = 'MIT'
__version__ = '0.0.3'

# Bari sensor of MS5637
sensor = ms5637.Chip()

host = "192.168.0.2"  # The BIG machine for the number grinding
port = 6421  # bari port
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    try:
        epochtime = time()
        humantime = datetime.fromtimestamp(epochtime).strftime('%Y-%m-%dT%H:%M:%S')
        pressure, temperature = sensor.get_data()
        print(humantime, pressure)

        outstring = pack('!d', *[pressure])  # .pack('!d', )
        # outstring = pack('!2d',*[pressure, temperature])
        # outstring = pack('!2d',*[epochtime, pressure])

        sock.sendto(outstring, (host, port))
        sleep(.1)
    # print(humantime, pressure)
    #    outstring = str(humantime) + ', ' + str(pressure)
    except OSError:
        sensor.__init__()
        pressure, temperature = sensor.get_data()
    except KeyboardInterrupt:
        sock.close()  # from os import _exit as dumbnrun
        dumbnrun(0)  # https://bytes.com/topic/python/answers/156121-os-_exit-vs-sys-exit
#
# Someday a cleaner Python interface will live here
#
# End
