import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import ms5637

__author__ = 'Moe'
__copyright__ = 'Copyright 2017  Moe'
__license__ = 'MIT'
__version__ = '0.0.2'

# Bari sensor of MS5637
sensor = ms5637.Chip()

plt.axis([0.0, 600.0, 100000, 102000])
# plt.axis([0.0, 600.0, 15.0, 45.0])  # Temp
plt.ion()

for i in range(600):
    #    sleep(2)
    pressure, temperature = sensor.get_data()

    plt.scatter(i, pressure)
    #    plt.scatter(i, temperature)
    plt.pause(.05)
