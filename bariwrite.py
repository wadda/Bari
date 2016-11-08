#!/usr/bin/python3
# coding=utf-8
"""reads barometric pressure sensor and writes it to a log
"""
import bari
from datetime import datetime
from time import time
from time import sleep

__author__ = 'Moe'
__copyright__ = 'Copyright 2016 Moe'
__license__ = 'MIT'
__version__ = '0.0.1'

sensor = bari.Chip()

bari_file = 'bari_data.csv'

try:
    while True:
        bari_data = open(bari_file, 'a')

        now = time()
        humantime = datetime.fromtimestamp(now).strftime('%Y-%m-%dT%H:%M:%SZ')
        pressure, _temperature = sensor.bari()
        outstring = str(humantime) + ', ' + str(pressure) + '\n'
        print(str(now) + ' ' + str(pressure))
        bari_data.writelines(outstring)
        sleep(0.07)

except KeyboardInterrupt:
    print('\nTerminated by user\nBari data written.\nGood Bye.\n')
finally:
    bari_data.close()
# End
