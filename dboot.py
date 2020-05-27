import esp, network, machine
machine.Pin(4,machine.Pin.IN,machine.Pin.PULL_DOWN)
network.WLAN(network.STA_IF).active(False)
esp.osdebug(True)
from structure import main
main.boot()