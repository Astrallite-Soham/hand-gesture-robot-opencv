import.network
import socket
from time import sleep
def setup.sta():
    wlan=network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("AndroidAP","isqz****")
    while not wlan.isconnected():
        sleep(5)
    ip_address=wlan.ifconfig()[0]
    print("IP Address", ip_address)
    return wlan
setup_sta()