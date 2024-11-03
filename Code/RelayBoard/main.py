import json
import os
import socket
import time

import network

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('PopcornE', 'XeThawr2Be')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# addr = ("192.168.164.255", 4911)


while True:
    if sta_if.isconnected():
        #TODO: Handle Exception
        message = json.loads(input())
        addr = (message["ip"], message["port"])
        client_socket.sendto(message["payload"], addr)
    else:
        print("Not Connected")
        time.sleep(1)