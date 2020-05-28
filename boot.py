import network, esp
network.WLAN(network.STA_IF).active(False)
esp.osdebug(None)