import machine

html = """<!DOCTYPE html>
<html>
<body>

<h2>Arduino Logo</h2>
<img src="alogo.gif" alt="Arduino">

</body>
</html>
"""
imOpen = open('alogo.gif')
image=imOpen.read()
imOpen.close()

import socket
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
        print(line2)
        if not line or line == b'\r\n':
            cl.write(html)
            #cl.close() commented, so that image can load
            break
        if line == b'GET /alogo.gif HTTP/1.1\r\n':
            cl.write(image)
            # cl.close() commented, so that image can load
            break
