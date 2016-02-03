import Adafruit_BBIO.GPIO as GPIO
from time import sleep
from subprocess import call

'''No es necesario especificar cuanto tiempo se queda dormido, porque el 
   script de los sensores espera el toque del swtich'''
sleep(10)
GPIO.cleanup()
sleep(2)
GPIO.setup("P9_11", GPIO.IN)
GPIO.setup("P9_13", GPIO.OUT)   
GPIO.wait_for_edge("P9_11", GPIO.FALLING) #esperando para activar el switch
print 'Hola'
flag = 1
conteo = 10      #cantidad de veces a intentar
while flag:
  GPIO.output("P9_13", GPIO.HIGH)
  sleep(0.5)
  GPIO.output("P9_13", GPIO.LOW)
  sleep(2)
  GPIO.cleanup()
  sleep(10)
  x = call("systemctl start sensor.service",shell=True)
  conteo -= 1
  if x == 0:
    flag = 0
  elif x != 0:
    call("systemctl start sensor.service",shell=True)
  elif conteo == 0: #se acabaron las oportunidades
   flag = 0
  break
  sleep(0.01)
  



