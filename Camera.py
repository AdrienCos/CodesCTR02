from picamera import PiCamera
from time import sleep

cam = PiCamera()

cam.resolution = (1280,720)
cam.framerate = 60

cam.start_preview()
sleep(2)
cam.start_recording('/home/pi/Desktop/vid.h264')
sleep(10)
cam.stop_recording()
cam.stop_preview()

