from structure import update, color, machine_data
import _thread as th
from time import sleep

def start():
  handle_server()
  try:
    print('System running')
  except:
    print('ERROR starting System')


def handle_server():
  print('get server_list')
  server_list = update.read_remote('server_list','https://raw.githubusercontent.com/marsex/asmon_structure/master/')
  server_list = server_list.text.split(',')
  print('Server #1:', server_list[0])
  
  host, port = server_list[0].split(':')
  
  th.start_new_thread(server_com,(host,port))
  print('continue...')


def server_com(host,port):
  print(color.green()+'\nStart server communication\n'+'IP:',host,'\nPORT:',port+'\n'+color.normal())
  json_data = machine_data.create()

  while True:
    address = socket.getaddrinfo(host, port)[0][-1]

    client_socket = socket.socket()
    client_socket.setblocking(False)

    try:
      client_socket.connect(address)
    except OSError as error:
      if error.args[0] not in [uerrno.EINPROGRESS, uerrno.ETIMEDOUT]:
        print('Error connecting', error)

    json_data = machine_data.get()
    attempts = 2

    while attempts:
      attempts=attempts-1
      print('try to send data: ', attempts)
      try:
        print('sending data')
        client_socket.sendall(bytes(str(json_data), 'UTF-8'))
        sleep(0.2)
        print('data sent')
        while True:
          buffer_data = client_socket.recv(2000)
          host_data = str(buffer_data)
          if host_data.find('null') == -1:
            parse_data(host_data)
          attempts = 0
          print('Got Data: ')
          break
      except OSError as e:
        if e.args[0] not in [uerrno.EINPROGRESS, uerrno.ETIMEDOUT]:
          print('**** ERROR writing ****', e)
          attempts = 0
      sleep(0.1)
    client_socket.close()


def parse_data(client_data):
  print(client_data)
  try:
    parsed_input = str(client_data[2:len(client_data)-1].replace("\'", "\""))
    print(parsed_input)
    command_json = ujson.loads(parsed_input)
    print(command_json)

    if command_json['command'] == 'output_state':
      update = command_json['update'].split('=')
      pin=int(update[0])-1
      state=int(update[1])
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
  except:
    print('error reading json')