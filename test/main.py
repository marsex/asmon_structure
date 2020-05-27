def web_page():
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  
  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p></body></html>"""
  return html

st_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
st_socket.bind(('', 80))
st_socket.listen(5)

while True:
    client, address = st_socket.accept()
    ip, port = str(address[0]), str(address[1])
    print('connection from ' + ip + ':' + port)
    client_file = client.makefile('rwb', 0)

    while True:
        line = client_file.readline()
        data = str(line).replace("b'",'').replace("'",'')
        
        print(data)
        if not line or line == b'\r\n':
            break
        #"b'GET /?@ssid:TP-LINK_56A8@ssid_psw:1234oooooo HTTP/1.1\r\n'"
        get_credentials = data.find('@credentials:')
        output_state= data.find('@output_state:')
        end_data = data.find('@end')
        
        response = web_page()
        
        if line == b'GET /logo.png HTTP/1.1\r\n':
            imOpen = open('/structure/logo.png')
            image=imOpen.read()
            imOpen.close()
            client.write(image)
        elif get_credentials != -1:
            print('Found credentials')
            c_data = data[get_credentials+len('@credentials:'): end_data]
            wifi.set_credentials(c_data)
            response = com_data.replace('$machine_data','@credentials_saved')
        elif output_state != -1:
            print('Found output command')
            c_data = data[output_state+len('@output_state:'): end_data]
            print('\n\t',c_data,'\n')
            response = com_data.replace('$machine_data',str(machine_data.get()))
        else:
            response = web_page()
        
    client.sendall(response)
    client.close()