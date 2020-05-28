from structure import off_sys, wifi
from time import sleep
import esp, machine
import _thread as th
th_new = th.start_new_thread

def boot():
    esp.osdebug(None)
    machine.freq()          # get the current frequency of the CPU
    machine.freq(240000000) # set the CPU frequency to 240 MHz
    print('\n\nStarting WiFi System\n\n')
    print(wifi.start())

    print('\n\nStarting OFFLINE System\n\n')
    print(off_sys.start())
    
boot()