import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.GPIO as GPIO
from time import sleep
from datetime import datetime
import math
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

def Conc_CO2(res_div,medida):
  #funcion para calcular la concentracion de CO2
  #pendiente = REACTION_VOLTAGE/(log(400) - log(1000))
  volts = (medida)*(1+res_div[0]/res_div[1])
  #if ((volts/DC_GAIN )>=ZERO_POINT_VOLTAGE):
  #  return -1
  #else:
  #return pow(10,((volts/DC_GAIN) - ZERO_POINT_VOLTAGE)/(pendiente + log(400)))
  conc = (191942657.449)*(math.e**(-0.00474*volts))
  return round(conc,1), volts

def Conc_CO(volt1):
  #funcion para calcular la concentracion de CO
  #RL es la resistencia de carga,volt1 el voltaje que se mide en el
  #se asume que el sensor es alimentado con 5V sino cambiar Vc

  Vc = 5  #voltaje de alimentacion
  Ro = 10 #kilo ohmios
  Rs_Ro = ((Vc/(volt1/1000)) - 1)*(RL/Ro)
  conc = 96.76*(Rs_Ro**(-1.54))
  return round(conc,1), Rs_Ro  
          
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
  voltajes_CO2 = []
  Rs_Ros = []
  times=[]
  values1=[]

  while True:
    volt = 1800*ADC.read("P9_40")    #mV CO2
    volt, voltaje_CO2 = Conc_CO2(res_div,DC_GAIN,volt)
    volt_1 = 1800*ADC.read("P9_39")  #mV CO
    volt_1,Rs_Ro = Conc_CO(volt_1)
    voltajes_CO2.append(voltaje_CO2)
    Rs_Ros.append(Rs_Ro)
    values.append(volt)
    values1.append(volt_1)
    #print values1,values
    times.append(datetime.now())
    sleep(READ_SAMPLE_INTERVAL)
    if len(values)==READ_SAMPLE_TIMES:
      #timesample=times[int(len(times)/2)]
      fecha = datetime.now()
      f.write('{0},{1},{2},{3},{4} \n'.format(fecha.isoformat(),
                           sum(values)/READ_SAMPLE_TIMES,
                           sum(values1)/len(values1),
                           sum(voltajes_CO2)/len(voltajes_CO2),
                           sum(Rs_Ros)/len(Rs_Ros)))
      f.flush()
      break
  sleep(0.01)  
      

    










