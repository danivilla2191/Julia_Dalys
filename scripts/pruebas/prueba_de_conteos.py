import Adafruit_BBIO.GPIO as GPIO
from time import sleep

GPIO.setup("P9_11", GPIO.IN)
GPIO.add_event_detect("P9_11", GPIO.FALLING)

conteo = 0
while True:
  if GPIO.event_detected("P9_11"):
    conteo += 1
    print conteo
  sleep(0.01)
    
 
