import Adafruit_BBIO.ADC as ADC
from time import sleep
import math
ADC.setup()

res_div = [22000.0,10000.0]      #divisor de voltaje
def Conc_CO2(res_div,medida):
  volts = (medida)*(1.0+(res_div[0]/res_div[1]))
  conc = (191942657.449)*(math.e**(-0.00474*volts))
  return round(conc,2)

def Conc_CO(volt1):
  #funcion para calcular la concentracion de CO
  #RL es la resistencia de carga,volt1 el voltaje que se mide en el
  #se asume que el sensor es alimentado con 5V sino cambiar Vc
  RL = 9.38
  Vc = 5  #voltaje de alimentacion
  Ro = 10 #kilo ohmios
  Rs_Ro = ((Vc/(volt1/1000)) - 1)*(RL/Ro)
  conc = 96.76*(Rs_Ro**(-1.54))
  return (conc,2)

while 1 :
  volt = 1800*ADC.read("P9_40")    #mV CO2
  volt = Conc_CO2(res_div,volt)    #conc de CO2
  volt1 = 1800*ADC.read("P9_39")   #mV CO
  volt1 = Conc_CO(volt1)           #conc de CO
  print("Concentracion de CO2: {0}, Voltaje Sensor de CO: {1}".format(
          volt, volt1))
  volt = Conc_CO2(res_div,volt)
  sleep(1)
