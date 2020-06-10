try:
  import usocket as socket
except:
  import socket

from machine import Pin
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = '1255'
password = '12551255'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

led = Pin(2, Pin.OUT)



html = """<!DOCTYPE html>
<html>
<body>

<h2>Arduino Logo</h2>
<img src="alogo.gif" alt="Arduino">

</body>
</html>
"""
imOpen = open('/structure/logo.png')
image=imOpen.read()
imOpen.close()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)
print('listening on', addr)

while True:
    cl, addr = s.accept()
    #print('client connected from', addr)
    cl_file = cl
    while True:
        line = cl_file.readline()
        line2=str(line)
        rr='nada'
        if not line or line == b'\r\n':
            print(line)
            cl.write(html)
            rr=' not line or line'
            #cl.close() commented, so that image can load
            break
        if line == b'GET /alogo.gif HTTP/1.1\r\n':
            cl.write(image)
            rr='alogo'
            # cl.close() commented, so that image can load
            break
    print(rr)
    
