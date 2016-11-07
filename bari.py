# coding=utf-8
"""The MS5637 has only five basic commands:
1. Reset
2. Read PROM (112 bit of calibration words)
3. D1 conversion (pressure)
4. D2 conversion (temperature)
5. Read ADC result (24 bit pressure / temperature
They are to be done in order. A loop can be shortened to steps 3-5
"""
from __future__ import division

from time import sleep

import smbus

__author__ = 'Moe'
__copyright__ = 'Copyright 2016  Moe'
__license__ = 'MIT'
__version__ = '0.0.1'

# MS5637 default address.
CHIP = 0x76
# Registers
# PROM Read 0XA0 to 0XAC
REGISTER_C0 = 0XA0  # CRC, and 'Factory defined'. e.g., [189, 225].
REGISTER_C1 = 0XA2  # Sensitivity
REGISTER_C2 = 0XA4  # Pressure Offset
REGISTER_C3 = 0XA6  # Temp Coefficient of Pressure Sensitivity
REGISTER_C4 = 0XA8  # Temp Coefficient of Pressure Offset
REGISTER_C5 = 0XAA  # Reference Temperature
REGISTER_C6 = 0XAC  # Temp Coefficient of Temperature

# Operating Modes     OSR256   OSR512 0SR1024 OSR2048 OSR4096 OSR8192
# Resolution        :   11    |  6.2 | 3.9   | 2.8   | 2.1   | 1.6    # Pascals
#                   :  0.012  | 0.009| 0.006 | 0.004 | 0.003 | 0.002  # Celsius
# Oversampling Ratio:    256  |  512 | 1024  | 2048  | 4096  | 8192
# Sampling rate  ms :    0.54 | 1.06 | 2.08  | 4.13  | 8.22  | 16.44  # Manufacturer data sheet
# delay sampling    :    2    |  4   |  6    |  10   |  18   |  34    # Recommended times from Arduino driver No idea.
# Pressure Convert=Address, delay sec # Temperature Convert Address incremented at function.
OSR256 = (0x40, 0.002)  # OSR-256   D1  # OSR256 = 0x50  # OSR-256   D2
OSR512 = (0x42, 0.004)  # OSR-512   D1  # OSR512 = 0x52  # OSR-512   D2
OSR1024 = (0x44, 0.006)  # OSR-1024  D1  # OSR1024 = 0x54  # OSR-1024  D2
OSR2048 = (0x46, 0.010)  # OSR-2048  D1  # OSR2048 = 0x56  # OSR-2048  D2
OSR4096 = (0x48, 0.018)  # OSR-4096  D1  # OSR4096 = 0x58  # OSR-4096  D2
OSR8192 = (0x4A, 0.034)  # OSR-8192  D1  # OSR8192 = 0x5A  # OSR-8192  D2

# Command keys
ADC_READ = 0x00
RESET = 0x1E


class Chip(object):
    """. . ."""

    def __init__(self, i2c_bus=1):
        self._device = smbus.SMBus(i2c_bus)
        self.reset()

    def reset(self):
        """
        The Reset sequence shall be sent once after power-on to make sure that the calibration PROM gets loaded
         into the internal register. It can be also used to reset the device PROM from an unknown condition.

        The read command for PROM shall be executed once after reset by the user to read the content of the calibration
        PROM and to calculate the calibration coefficients. There are in total 7 addresses resulting in a total memory
        of 112 bit.
        """
        self._device.write_byte(CHIP, RESET)
        self._read_calibration_data()

    def _read_calibration_data(self):
        # self.CRC, self.FACTORY = self._device.read_byte_data(CHIP, REGISTER_C0, 2)  # CRC and Factory settings

        data = self._device.read_i2c_block_data(CHIP, REGISTER_C1, 2)  # Sensitivity self.SENS
        self.SENS = data[0] * 256 + data[1]

        data = self._device.read_i2c_block_data(CHIP, REGISTER_C2, 2)  # Pressure Offset self.OFF
        self.OFF = data[0] * 256 + data[1]

        data = self._device.read_i2c_block_data(CHIP, REGISTER_C3, 2)  # Temp Coefficient of Pressure Sensity self.TCF
        self.TCF = data[0] * 256 + data[1]

        data = self._device.read_i2c_block_data(CHIP, REGISTER_C4, 2)  # Temp Coefficient of Pressure Offset self.TCO
        self.TCO = data[0] * 256 + data[1]

        data = self._device.read_i2c_block_data(CHIP, REGISTER_C5, 2)  # Reference Temperatureself.TREF
        self.TREF = data[0] * 256 + data[1]

        data = self._device.read_i2c_block_data(CHIP, REGISTER_C6, 2)  # Temp Coefficient of Temperature self.TEMPSENS
        self.TEMPSENS = data[0] * 256 + data[1]

    def _read_raw_pressure(self, osr=OSR256):
        """Request converted data.  Waits times used im an Arduino driver before reading that request."""
        self._device.write_byte(CHIP, osr[0])
        sleep(osr[1])

        raw_value = self._device.read_i2c_block_data(CHIP, ADC_READ, 3)  # raw_value = MSB2, MSB1, LSB
        raw_pressure = raw_value[0] * 65536 + raw_value[1] * 256 + raw_value[2]  # should 256 become OSR value?
        return raw_pressure  # D1

    def _read_raw_temperature(self, osr=OSR256):
        """Request converted data.  Waits times used im an Arduino driver before blah, blah, blah."""
        tempsample = 16 + osr[0]  # Increment Temperature convert command address from Pressure address
        self._device.write_byte(CHIP, tempsample)  # sh/could stay with OSR256.
        sleep(osr[1])  # Only assuming the delay requirement for Temperature is the same as Pressure.

        raw_value = self._device.read_i2c_block_data(CHIP, ADC_READ, 3)  # raw_value = MSB2, MSB1, LSB
        raw_temperature = raw_value[0] * 65536 + raw_value[1] * 256 + raw_value[2]
        return raw_temperature  # D2

    def bari(self):
        """Convert raw date into calibrated pressure (pascals) and temperature (degrees)
        """
        raw_pressure = self._read_raw_pressure()  # TODO: OSR settings
        raw_temperature = self._read_raw_temperature()
        delta_time = raw_temperature - self.TREF * 256
        offset = self.OFF * 131072 + (self.TCO * delta_time) / 64
        sens = self.SENS * 65536 + (self.TCF * delta_time) / 128
        offset2 = 0
        sens2 = 0
        T2 = 0  # Temp scaling
        TEMP = 2000 + delta_time * self.TEMPSENS / 8388608
        if TEMP > 2000:
            T2 = 5 * delta_time * delta_time / 274877906944
            offset2 = 0
            sens2 = 0
        elif TEMP < 2000:
            T2 = 3 * (delta_time * delta_time) / 8589934592
            offset2 = 61 * ((TEMP - 2000) * (TEMP - 2000)) / 16
            sens2 = 29 * ((TEMP - 2000) * (TEMP - 2000)) / 16
            if TEMP < -1500:
                offset2 += 17 * ((TEMP + 1500) * (TEMP + 1500))
                sens2 += 9 * ((TEMP + 1500) * (TEMP + 1500))

        TEMP -= T2
        offset -= offset2
        sens -= sens2
        pressure = ((((raw_pressure * sens) / 2097152) - offset) / 32768.0)
        temperature = TEMP / 100.0
        return pressure, temperature


if __name__ == '__main__':
    chip = Chip()
    for i in range(1, 10):
        pressure, temperature = chip.bari()
        print('Pascals: {}   TempC: {}'.format(pressure, temperature))
        sleep(1)
#
# Someday a cleaner Python interface will live here
#
# End
