import json
import time

import serial_manager
import vicon_manager


mgr = vicon_manager.ViconConnection()
ser = serial_manager.SerialSender('COM3')

targetIP = "192.168.164.79"
targetPort = 4911

while True:
    ser.send_msg_dict_to_addr(targetIP, targetPort, mgr.get_objects_in_scene())
    print("updating")