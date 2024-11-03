import json
import serial

class SerialSender:
    def __init__(self, port:str):
        self.device = serial.Serial(port, 115200)

    def send_msg_dict_to_addr(self, ip:str, port:int, payload:dict):
        payload = json.dumps(payload).replace('\\', '\\\\').replace('\r', '\\r').replace('\n', '\\n')
        out = {'ip':ip, 'port':port, 'payload':payload}
        out = json.dumps(out)
        self.device.write((out + "\r\n").encode('ASCII'))

    # TODO Maybe add a checksum to make sure packets reaches its destination correctly
