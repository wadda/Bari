import numpy as np
import matplotlib.pyplot as plt
import bari
from time import sleep

sensor = bari.Chip()

plt.axis([0.0, 600.0, 100000, 102000])
# plt.axis([0.0, 600.0, 15.0, 45.0])  # Temp
plt.ion()

for i in range(600):
    #    sleep(2)
    pressure, temperature = sensor.bari()

    plt.scatter(i, pressure)
    #    plt.scatter(i, temperature)
    plt.pause(.05)
