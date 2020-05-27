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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('', 80))

s.listen(5)

while True:
    client, address = s.accept()
    print('Got a clientection from %s' % str(address))
    request = client.recv(1024)
    request = str(request)

    client_file = client.makefile('rwb', 0)
    print('Content = %s' % request)
    led_on = data.find('/?led=on')
    led_off = data.find('/?led=off')
    if led_on != -1:
        print('LED ON')
        led.value(1)
    if led_off == -1:
        print('LED OFF')
        led.value(0)    
    response = web_page()
    client.send('HTTP/1.1 200 OK\n')
    client.send('Content-Type: text/html\n')
    client.send('Connection: close\n\n')
    client.sendall(response)
    client.close()