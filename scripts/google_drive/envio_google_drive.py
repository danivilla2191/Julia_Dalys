import json
import sys
import time
from datetime import datetime,timedelta
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import subprocess

#global el diccionario que guarda la informacion de los archivos subidos
global inf 

def serializador(sign,file):
  '''Esta funcion se encarga de serializar un string con los datos del ultimo
     archivo que fue subido a google drive'''
  #sign se encarga de decir si se va a guardar el archivo o se va a abrir
  #file string con el nombre del ultimo archivo  que se subio al drive
  from pickle import dump, load
  
  #contando lineas para verificar que todas las lineas de un mismo archivo
  #fueron subidas
  lineas = 0 
  for line in open(file): lineas += 1

    if sign=='guardar':
       with open('google.pickle','wb') as f:
          inf = {'lineas':str(lineas),'archivo':file}
          dump(inf,f)

    if sign=='abrir':
       with open("google.pickle",'rb') as f:
          inf = load(f)

   

