from structure import update, color, machine_data
import _thread as th
import socket
import uerrno
import ujson
from machine import Pin
from time import sleep

def start():
  print(color.yellow()+'\n Starting asmon_system')
  server_list = get_server_list()
  host, port = server_list[0].split(':')
  if host != 'null':
    print(color.green()+'\nStart server communication\n'+'IP:',host,'\nPORT:',port+'\n'+color.normal())    
    try:
      address = socket.getaddrinfo(host, port)[0][-1]
      print(address)
      th.start_new_thread(start_com,(address,"hola"))
    except:
      print(color.red()+'Error getting addr info from', host,port)
  else:
    print(color.red()+'Error starting asmon_system')

def get_server_list():
  server_request = update.read_remote('server_list','https://raw.githubusercontent.com/marsex/asmon_structure/master/')
  try:
    server_list = server_request.text.split(',')
    i = 0
    for server in server_list:
      print('Server #'+str(i)+':', server)
      i = i + 1
    return server_list
  except: 
    return ['null:null']

def start_com(address,hola):
  json_data = machine_data.create()
  while True:
    #print(color.blue()+'{')

    client_socket = socket.socket()
    client_socket.setblocking(0)
    try:
      #print('\tConnect to',address)
      client_socket.connect(address)
    except OSError as error:
      if error.args[0] not in [uerrno.EINPROGRESS, uerrno.ETIMEDOUT]:
        print(color.red()+'**** Error connecting ****', error+color.normal())
        
    attempts = 10
    json_data = machine_data.get()
    while attempts:
      attempts=attempts-1
      #print('\t{\n\t\tAttempt to send data: ', attempts)
      try:
        #print('\t\t{\n\t\t\tSending data')
        client_socket.sendall(bytes(str(json_data), 'UTF-8'))
        #print('\t\t\tData Sent\n\t\t\t{')
        sleep(0.2)
        #print('\t\t\t\tWait for response')  
        while True:
          buffer_data = client_socket.recv(2000)
          host_data = str(buffer_data)
          if host_data.find('null') == -1:
            parse_data(host_data)
          attempts = 0
          #print('\t\t\t\tGot response') 
          break
        #print(color.red()+'\t\t\t}')
      except OSError as error:
        if error.args[0] not in [uerrno.EINPROGRESS, uerrno.ETIMEDOUT]:
          print(color.red()+'\t\t\t**** ERROR writing ****\n\t\t\t', error)
          attempts = 0
      #print(color.red()+'\t\t}')
      sleep(0.1)
      break  
    client_socket.close()
    #print(color.red()+'\t}\n')
    #print(color.red()+'}'+color.normal())
    sleep(0.1)

def parse_data(client_data):
    print(client_data)
  #try:
    parsed_input = str(client_data[2:len(client_data)-1].replace("\'", "\""))
    #print(parsed_input)
    command_json = ujson.loads(parsed_input)
    #print(command_json)

    if command_json['command'] == 'output_state':
      update = command_json['update'].split('=')
      pin=int(update[0])-1
      state=int(update[1])
      out_gpio = machine_data.out_pins()
      Pin(out_gpio[pin], value=state)

    if command_json['command'] == 'dht1':
      update = command_json['update'].split(',')
      print(update)
      for x in update:
        objeto = x.split('=')
        machine_data.set_double('dht1',objeto[0],objeto[1])
        
    if command_json['command'] == 'remote_update':
      update_info = command_json['update'].split(',')
      print('try to update', update_info)
      from structure import update
      update.remote(update_info[0],update_info[1],update_info[2])
  #except:
    #print('error reading json')
