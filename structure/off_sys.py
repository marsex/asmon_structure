import network
import socket
from time import sleep
from structure import machine_data, wifi
machine_data.create()


def start():
    print('Starting AP System')
    station = network.WLAN(network.STA_IF)
    station.active(True)
    ap_server()
    print('ok')
  

def create_html():
    try:
        scan_list = station.scan()
    except:
        scan_list = 'null'

    if scan_list == 'null':
        return 'scan error'
        
    tr_swap=""
    tr_format="""
    <tr>
        <td onclick="set_ssid(this)">$ssid</td>
        <td class=$signal_state style="width:120px">$signal_state</td>
    </tr>
    """

    for wifi_net in scan_list:
        net_signal=int(str(wifi_net[3]).replace('-',''))
        net_ssid=str(wifi_net[0]).replace("b'",'')
        net_ssid=net_ssid.replace("'",'')
        signal_state=''
        if net_signal <= 66:
          signal_state = "Excelente"

        if net_signal >= 67:
          signal_state = "Buena"
          
        if net_signal >= 80:
          signal_state = "Mala"
          
        tr_done = tr_format.replace('$ssid',net_ssid).replace('$signal_state',signal_state)
        tr_swap = tr_swap + tr_done

    credentials_state, cred_ssid, cred_psw = wifi.get_credentials()
    print(tr_swap)
    file = open('/structure/index.html','r')
    html = file.read()
    html = html.replace('$tr_swap',tr_swap).replace('$cred_ssid',cred_ssid).replace('$cred_psw',cred_psw)
    file.close()
    return html

def st_server():
    print('\n\nStarting ST Server\n-----------------------')
    print('Check WiFi credentials')
    credentials_state, cred_ssid, cred_psw = wifi.check_credentials()
    while credentials_state == False:
        credentials_state, cred_ssid, cred_psw = wifi.check_credentials()
        sleep(1)
        pass
    
    print('Got WiFi credentials')
    wifi.connect(cred_ssid,cred_psw)
    
    while station.isconnected() == False:
        pass
    
    print('Connection successful')
    print(station.ifconfig())
    
    
def ap_server():
  #  try:
    port=80
    ap_wlan = network.WLAN(network.AP_IF)
    ap_wlan.active(True)
    ap_wlan.config(essid='ASMON AP System')
    ap_wlan.config(authmode=3, password='12551255')

    print('Access point created')
    print('AP Network data: ',ap_wlan.ifconfig())
    
    ap_localhost=ap_wlan.ifconfig()[0]            #get ip addr

    print('Got IP')
    ap_socket = socket.socket()                   #create socket
    print('Socket created')
    ap_socket.bind((ap_localhost,port))           #bind ip and port
    print('Socket bind complete')
    ap_socket.listen(1)                           #listen message
    print('Socket now listening on port:', port)      

    #Set the value of the given socket option
    ap_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    html=create_html()
    
    com_data="""
    <html>
        <input id="esp_data" style="padding: 8px 8px; display: block;width: 93.6%;" value="$machine_data" disabled>
        <script>
            machine_data = document.getElementById('esp_data').value
            window.parent.document.getElementById('esp_data').value = machine_data; 
        </script>
    </html>
    """
    
    while True:
        client, address = ap_socket.accept()
        ip, port = str(address[0]), str(address[1])
        print('connection from ' + ip + ':' + port)
        client_file = client.makefile('rwb', 0)
  
        while True:
            line = client_file.readline()
            data = str(line).replace("b'",'').replace("'",'')
            response = html
            
            print(data)
            if not line or line == b'\r\n':
                break
            #"b'GET /?@ssid:TP-LINK_56A8@ssid_psw:1234oooooo HTTP/1.1\r\n'"
            get_credentials = data.find('@credentials:')
            output_state= data.find('@output_state:')
            end_data = data.find('@end')
            
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
                response = create_html()
            
        client.sendall(response)
        client.close()
   # except:
       # if(ap_socket):
         #   ap_socket.close()
        #ap_wlan.disconnect()
       # ap_wlan.active(False)
       # print('ap_closed')
    

def send_json(client, data_json):
    import json
    data_json = json.dumps(data_json)
    response_headers = {'Access-Control-Allow-Origin': '*','Content-Type': 'application/json','Content-Length': len(data_json),'Connection': 'close',}
    response_headers_raw = ''.join('%s: %s\r\n' % (k, v) for k, v in response_headers.items())
    response_proto = 'HTTP/1.1'
    response_status = '200'
    response_status_text = 'OK' 
    r = '%s %s %s\r\n' % (response_proto, response_status, response_status_text)

    client.send(r.encode())
    client.send(response_headers_raw.encode())
    client.send('\r\n'.encode())  # to separate headers from body
    client.sendall(data_json.encode())
