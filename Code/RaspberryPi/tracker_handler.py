import json
import socket
import threading

import numpy as np

PORT = 4911

ROBOT_NAME = "Robot"

class TrackerHandler:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', PORT))
        self.thread = threading.Thread(target=self._process_socket_data, daemon=True)
        self.thread.start()

        self.robot_track = None

    def _process_socket_data(self):
        while True:
            raw_data, addr = self.sock.recvfrom(16384)
            try:
                data = json.loads(raw_data.decode('ascii'))
                if ROBOT_NAME in data and len(data[ROBOT_NAME]) > 0:
                    self.robot_track = data[ROBOT_NAME][0]
            except json.decoder.JSONDecodeError as exc:
                print(exc)
                print(f"\033[91m{raw_data}\033[91m")
    
    def get_robot_track(self):
        while self.robot_track is None:
            pass
        return self.robot_track

    def _print_robot_track(self):
        while self.robot_track is None:
            pass
        print(self.robot_track['location'])


