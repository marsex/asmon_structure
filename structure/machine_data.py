import machine
import dht
import time
import uerrno
from machine import Pin

inp_gpio=[35,34,39,36,21,19,18,5,17,16,4]
out_gpio=[32,33,25,26,27,14,12,13]

dht1 = dht.DHT22(Pin(15, Pin.IN, Pin.PULL_UP))
dht2 = dht.DHT22(Pin(22, Pin.IN, Pin.PULL_UP))

def gpio_pins():
  return out_gpio, inp_gpio

def out_pins():
  return out_gpio

def inp_pins():
  return inp_gpio


def set_double(arg1,arg2,arg3):
  global machine_data
  try:
    machine_data[arg1][arg2] = arg3
  except:
    return 'error manipulating machine data, \narg1:', arg1, '\narg2:', arg2, '\narg3:', arg3


def parse_data(command_json):
    #print(client_data)
  #try:
    #parsed_input = str(client_data[2:len(client_data)-1].replace("\'", "\""))
    #print(parsed_input)
    #command_json = ujson.loads(client_data)
    print(command_json)

    if command_json['command'] == 'output_state':
      update = command_json['update'].split('=')
      pin=int(update[0])-1
      state=int(update[1])
      out_gpio = out_pins()
      Pin(out_gpio[pin], value=state)

    if command_json['command'] == 'dht1':
      update = command_json['update'].split(',')
      print(update)
      for x in update:
        objeto = x.split('=')
        set_double('dht1',objeto[0],objeto[1])
        
    if command_json['command'] == 'remote_update':
      update_info = command_json['update'].split(',')
      print('try to update', update_info)
      from structure import update
      update.remote(update_info[0],update_info[1],update_info[2])
  #except:
    #print('error reading json')
    
    
def get():
  global machine_data
  input_state = [Pin(i, Pin.IN).value() for i in inp_gpio]
  output_state = [Pin(i, Pin.OUT).value() for i in out_gpio]
  
  machine_data['dht1']['tmp']=dht1.temperature()
  machine_data['dht1']['hmd']=dht1.humidity()
  machine_data['dht2']['tmp']=dht2.temperature()
  machine_data['dht2']['hmd']=dht2.humidity()
  machine_data['uptime']=str(time.time())
  machine_data['gpio']['input_state']=input_state
  machine_data['gpio']['output_state']=output_state
  
  return machine_data


def create():
  global machine_data
  machine_data = {
    "command":"null",
    "version":"v0.9.1.1",
    "platform":"asmon",
    "uptime":str(time.time()),
    "user":"esp02",
    "gpio":{
      "input_enable":[0,0,1,0,0,0,0,0],
      "input_state":[0,0,1,0,0,0,0,0],
      "input_prog":[0,0,2,0,0,0,0,0],
      "output_enable":[1,1,1,1,1,1,1,1],
      "output_state":[0,0,0,0,0,1,0,0],
      "output_prog":[0,0,0,0,0,0,0,0]
    },
    "dht1":{
      "tmp_enable":0,
      "tmp":0,
      "tmp_salida":3,
      "tmp_set":0,
      "tmp_on_time":0,
      "tmp_on_tick":0,
      "tmp_off_time":0,
      "tmp_off_tick":0,
      "tmp_interval":0,
      "tmp_tick":0,
      "hmd_enable":0,
      "hmd":0,
      "hmd_salida":3,
      "hmd_set":0,
      "hmd_on_time":0,
      "hmd_on_tick":0,
      "hmd_off_time":0,
      "hmd_off_tick":0,
      "hmd_interval":0,
      "hmd_tick":0
    },
    "dht2":{
      "tmp_enable":0,
      "tmp":0,
      "tmp_salida":3,
      "tmp_set":0,
      "tmp_on_time":0,
      "tmp_on_tick":0,
      "tmp_off_time":0,
      "tmp_off_tick":0,
      "tmp_interval":0,
      "tmp_tick":0,
      "hmd_enable":0,
      "hmd":0,
      "hmd_salida":3,
      "hmd_set":0,
      "hmd_on_time":0,
      "hmd_on_tick":0,
      "hmd_off_time":0,
      "hmd_off_tick":0,
      "hmd_interval":0,
      "hmd_tick":0
    }
  }
  return get()
