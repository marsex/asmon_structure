import network, socket, gc
from time import sleep
from structure import machine_data, wifi
import _thread as th
th_new = th.start_new_thread
machine_data.create()

def start():
    #th_new(ap_server,())
    th_new(st_server,())
    return '\n\nOFFLINE System Running\n\n'


def st_server():
    print('\n\nStarting ST Server\n-----------------------')
    print('Check WiFi credentials')
    credentials_state, cred_ssid, cred_psw = wifi.get_credentials()
    
    while credentials_state == False:
        credentials_state, cred_ssid, cred_psw = wifi.get_credentials()
        sleep(1)
        pass
    
    print('Got WiFi credentials')
    wifi_connected = wifi.connect(cred_ssid,cred_psw)
    
    while wifi_connected == False:
        pass
    
    print('Connection successful')    
    
    while True:
        port=80
        wlan_ip = network.WLAN(network.STA_IF).ifconfig()[0]
        
        st_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        st_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        st_socket.bind((wlan_ip, port))
        st_socket.listen(5)
        
        
        response=create_html()
        
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
            gc.collect()
            client, address = st_socket.accept()
            ip, port = str(address[0]), str(address[1])
            
            print('connection from ' + ip + ':' + port)
            client_file = client.makefile('rwb', 0)
      
            while True:
                line = client_file.readline()
                if not line or line == b'\r\n':
                    break   
    
                #data = str(line).replace("b'",'').replace("'",'')
                #print(data)
                response = handle_client(com_data,response,line,client)
                
            client.sendall(response)
            client.close()
    
def ap_server():
    print('\n\nStarting AP System\n\n')
    while True:
        port=80
        ap_wlan = network.WLAN(network.AP_IF)
        ap_wlan.active(True)
        ap_wlan.config(essid='ASMON AP System')
        ap_wlan.config(authmode=3, password='12551255')
        ap_localhost=ap_wlan.ifconfig()[0]            #get ip addr

        ap_socket = socket.socket()                   #create socket
        ap_socket.bind((ap_localhost,port))           #bind ip and port
        ap_socket.listen(1)                           #listen message
        ap_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        print('Socket now listening on port:', port)

        response=create_html()
        
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
            gc.collect()
            client, address = ap_socket.accept()
            ip, port = str(address[0]), str(address[1])
            print('connection from ' + ip + ':' + port)
            client_file = client.makefile('rwb', 0)
            th_new(handle_client,(com_data,response,line,client))
    
def handle_client(com_data,response,line,client):
    data = str(line).replace("b'",'').replace("'",'')
    send_html = data.find('GET / HTTP/1.1')
    data_com = data.find('@data_com')
    get_credentials = data.find('@credentials:')
    output_state= data.find('@output_state:')
    end_data = data.find('@end')
    if send_html != -1:
        response = create_html()
        print(data)
    if data_com != -1:  
        esp_data = machine_data.get()
        response = com_data.replace('$machine_data',str(esp_data['gpio']))
        print(data)

    if line == b'GET /logo.png HTTP/1.1\r\n':
        print('write logo')
        imOpen = open('/structure/logo.png')
        image=imOpen.read()
        imOpen.close()
        client.write(image)
        print(data)
        
    if get_credentials != -1:
        print('Found credentials')
        c_data = data[get_credentials+len('@credentials:'): end_data]
        wifi.set_credentials(c_data)
        response = com_data.replace('$machine_data','@credentials_saved')
        print(data)
    
    if output_state != -1:
        print('Found output command')
        c_data = data[output_state+len('@output_state:'): end_data]
        print('\n\t',c_data,'\n')
        esp_data = machine_data.get()
        command_json={'command':'output_state','update':c_data}
        machine_data.parse_data(command_json)
        response = com_data.replace('$machine_data',str(esp_data['gpio']['output_state']))
        
        print(data)
    
    
def create_html():
    print('\n\nget_networks')
    scan_list = wifi.get_networks()
    
    tr_swap=""
    tr_format="""
    <tr>
        <td onclick="set_ssid(this)">$ssid</td>
        <td class=$signal_state style="width:120px">$signal_state</td>
    </tr>
    """
    if len(scan_list) != 0:
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
    gc.collect()
    file = open('/structure/index.html','r')
    html = file.read()
    html = html.replace('$tr_swap',tr_swap).replace('$cred_ssid',cred_ssid).replace('$cred_psw',cred_psw)
    file.close()
    return html
    
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
