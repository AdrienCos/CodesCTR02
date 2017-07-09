# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# LIS331HH
# This code is designed to work with the LIS331HH_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Accelorometer?sku=LIS331HH_I2CS#tabs-0-product_tabset-2

import smbus
import time
from math import sqrt

# Get I2C bus
bus = smbus.SMBus(1)

# LIS331HH address, 0x18(24)
# Select control register1, 0x20(32)
#		0x27(39)	Power ON mode, Data rate selection = 50 Hz
#					X, Y, Z-Axis enabled
bus.write_byte_data(0x19, 0x20, 0x27)
# LIS331HH address, 0x18(24)
# Select control register4, 0x23(35)
#		0x00(00)	Continous update, Full-scale selection = +/-6g
bus.write_byte_data(0x19, 0x23, 0x00)

time.sleep(0.5)

while(True):
        # LIS331HH address, 0x18(24)
        # Read data back from 0x28(40), 2 bytes
        # X-Axis LSB, X-Axis MSB
        data0 = bus.read_byte_data(0x19, 0x28)
        data1 = bus.read_byte_data(0x19, 0x29)

        # Convert the data
        xAccl = data1 *  256 + data0
        if xAccl > 32767 :
                xAccl -= 65536

        # LIS331HH address, 0x18(24)
        # Read data back from 0x2A(42), 2 bytes
        # Y-Axis LSB, Y-Axis MSB
        data0 = bus.read_byte_data(0x19, 0x2A)
        data1 = bus.read_byte_data(0x19, 0x2B)

        # Convert the data
        yAccl = data1 *  256 + data0
        if yAccl > 32767 :
                yAccl -= 65536

        # LIS331HH address, 0x18(24)
        # Read data back from 0x2C(44), 6 bytes
        # Z-Axis LSB, Z-Axis MSB
        data0 = bus.read_byte_data(0x19, 0x2C)
        data1 = bus.read_byte_data(0x19, 0x2D)

        # Convert the data
        zAccl = data1 *  256 + data0
        if zAccl > 32767 :
                zAccl -= 65536

        # Output data to screen
        #print(xAccl / 5400. , yAccl / 5400. , zAccl / 5400.)
	norme = sqrt(xAccl**2 + yAccl**2 + zAccl**2)
	print norme / 5400
        time.sleep(0.02)
