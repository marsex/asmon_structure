import network
import socket
import _thread as th
from time import sleep
th_new = th.start_new_thread
scan_list = []
def start():
    network.WLAN(network.STA_IF).active(True)
    th_new(scan_networks,())
    return '\n\nWiFi System Running\n\n'

def scan_networks():
    global scan_list
    station = network.WLAN(network.STA_IF)
    while True:
        try:
            #print('Scanning networks')
            scan_list = station.scan()
            #print(scan_list)
        except:
            print('scan failed')
        sleep(5)

def get_networks():
    global scan_list
    print(scan_list)
    return scan_list

def get_credentials():
  global cred_ssid, cred_psw
  file = open("/structure/credentials","r")
  data = file.read()
  file.close()

  cred_ssid=data.split(",")[0]
  cred_psw=data.split(",")[1]
  
  if cred_ssid == 'null':
    return False,cred_ssid,cred_psw
  else:
    return True,cred_ssid,cred_psw
    

def set_credentials(c_data):
    print('Got credentials: ', c_data)
    print('Saving credentials...')
    file = open("/structure/credentials","w")
    file.write(c_data)
    file.close()
    print('Credentials Saved')
  

def connect(cred_ssid,cred_psw):
    print('\n{\n\tConnecting to network: ' +cred_ssid)
    st_wlan = network.WLAN(network.STA_IF)
    st_wlan.active(True)

    if cred_ssid != 'null':
        if not st_wlan.isconnected():
            st_wlan.connect(cred_ssid,cred_psw)
            while not st_wlan.isconnected():
                pass
            print('\tConnected, st_wlan:', st_wlan.ifconfig(), '\n}\n')
            return True
        else:
            print('\tAlready connected to:', cred_ssid, '\n\t', st_wlan.ifconfig(),'\n}\n')
            return True
    else:
        try:
            print('\n{\n\treconnecting to network: ' +cred_ssid)
            if not st_wlan.isconnected():
                st_wlan.connect()
                while not st_wlan.isconnected():
                    pass
                print('\tConnected, st_wlan:', st_wlan.ifconfig(), '\n}\n')
                return True
            else:
                print('\tAlready connected to:', st_wlan.ifconfig(), '\n}\n')
                return True
        except:
            print('failed to reconnect')
            print('get wifi credentials')
            return False
          
      