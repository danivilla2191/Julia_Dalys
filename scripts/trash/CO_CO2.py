import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.GPIO as GPIO
from time import sleep
from datetime import datetime
from math import log
from subprocess import check_output,call
import Adafruit_DHT

#cerrando servicios que pueden generar conflicto al inicio
call("systemctl stop humedad.service",shell=True)
call("systemctl stop contador.service",shell=True)
call("systemctl stop espera.service",shell=True)

ADC.setup()
GPIO.cleanup()    #por si acaso algun otro servicio no limpio algun pin
GPIO.setup("P9_11", GPIO.IN)
GPIO.setup("P9_13", GPIO.OUT)
GPIO.add_event_detect("P9_11", GPIO.FALLING)

filename = '/root/datos/CO_CO2/{}'   #direccion en donde se guardan los datos

global DC_GAIN, RL
#parametros de los sensores
DC_GAIN = 8.5              #ganancia del amplificador
READ_SAMPLE_INTERVAL = 0.05  #muestras que se van a tomar
READ_SAMPLE_TIMES = 3600      #tiempo entre cada muestra
ZERO_POINT_VOLTAGE = 0.324 #sensor de CO2 400ppm
REACTION_VOLTAGE = 0.020   #sensor de CO2 cambio de 400 de aire a 1000 ppm
res_div = [22000,10000]    #resistencias utilizadas en el sensor de CO2, la segunda es la resistencia
                           #de donde se toma el voltaje que va al beaglebone
sample_int = 2
RL = 9.38        #Resistencia del potenciometro del sensor de CO

def Conc_CO2(res_div,REACTION_VOLTAGE,ZERO_POINT_VOLTAGE,medida):
  #funcion para calcular la concentracion de CO2
  pendiente = REACTION_VOLTAGE/(log(400) - log(1000))
  volts = (medida/1000)*(1+ res_div[0]/res_div[1])
  #if ((volts/DC_GAIN )>=ZERO_POINT_VOLTAGE):
  #  return -1
  #else:
  return pow(10,((volts/DC_GAIN) - ZERO_POINT_VOLTAGE)/(pendiente + log(400)))

def Con_CO(volt1):
  #funcion para calcular la concentracion de CO
  #RL es la resistencia de carga,volt1 el voltaje que se mide en el
  #se asume que el sensor es alimentado con 5V sino cambiar Vc

  Vc = 5  #voltaje de alimentacion
  k1 = 108.31 #intercepto 
  Ro = 10     #kilo ohmios
  Rs_Ro = ((Vc/volt1) - 1)*(RL/Ro)
  
  '''#Obteniendo la humedad y la temperatura
  count = 1
  while True:
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, "P8_11")
    if humidity is not None and temperature is not None:
      break
    else:
      if count==2:
        humidity, temperature = None
        break
      continue
    count+=1
    time.sleep(0.01)
  
  #correccion por humedad y temperatura      
  if humidity is not None and temperature is not None:
     Rs_Ro = Rs_Ro - (0.00012*pow(temperature,2) - 0.012*temperature + 1.045)
     #aplicando una regla de tres
     Rs_Ro = humidity*(Rs_Ro)/85
  if humidity is None and temperature is None:
     Rs_Ro = Rs_Ro
  '''
  return pow(Rs_Ro/26.03,-(1/0.7))
          
flag = 0
#la ejecucion continua cuando el usuario presiona el switch
while True:
  if GPIO.event_detected("P9_11"):
    GPIO.output("P9_13", GPIO.HIGH)
    #call("systemctl start contador.service",shell=True)
    sleep(2)
    call("systemctl start humedad.service",shell=True)
    GPIO.output("P9_13", GPIO.LOW)
    GPIO.cleanup()
    sleep(2)
    break 
  sleep(0.01)

sleep(15)
call("systemctl start contador.service",shell=True)

hour = datetime.now().hour
while 1:  
  dateobj=datetime.now()
  oldhour=hour
  hour=dateobj.hour

  f = open(filename.format(str(dateobj.date())),'a')
  
  #nuevo archivo cuando comienza un nuevo dia
  if (hour==0) and (oldhour==23):
    f.close()
    f = open(filename.format(str(dateobj.date())),'a')

  timenow=datetime.now()
  values=[]
  times=[]
  values1=[]

  while True:
    volt = 1800*ADC.read("P9_40")    #mV CO2
    volt = Conc_CO2(res_div,REACTION_VOLTAGE,ZERO_POINT_VOLTAGE,volt)
    volt_1 = 1800*ADC.read("P9_39")  #mV CO
    values.append(volt)
    values1.append(volt_1)
    #print values1,values
    times.append(datetime.now())
    sleep(READ_SAMPLE_INTERVAL)
    if len(values)==READ_SAMPLE_TIMES:
      #timesample=times[int(len(times)/2)]
      fecha = datetime.now()
      f.write('{0},{1},{2} \n'.format(fecha.isoformat(),
                           sum(values)/READ_SAMPLE_TIMES,sum(values1)/len(values1)))
      f.flush()
      break
  sleep(0.01)  
      

    










