from adxl345 import ADXL345

adx = ADXL345()

axes = adx.getAxes(True)
print (axes)
