import json
import math
import socket
import threading

import gripper_handler 
import motor_handler

PORT = 4912

class UnityHandler:
    def __init__(self, gripperHandler: gripper_handler.GripperHandler, 
            motors: motor_handler.MotorHandler):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gripperHandler = gripperHandler
        self.motors = motors
        self.sock.bind(('', PORT))
        self.target_gripper_pan = self.gripperHandler.get_gripper_pan()
        self.target_gripper_tilt = self.gripperHandler.get_gripper_tilt()
        self.last_data = {}
        self.update_thread = threading.Thread(target=self.listen, daemon=True)
        self.update_thread.start()

    def listen(self):
        self.sock.listen(5)
        while True:
            conn, addr = self.sock.accept()
            while True:
                raw = conn.recv(1024)
                if raw is None:
                    self.last_data = {}
                    break
                if raw == b"":
                    self.last_data = {}
                    break
                raw = raw.decode('UTF-8').split('\n')
                if len(raw) < 2:
                    continue
                else:
                    raw = raw[1]
                if raw is None or raw == '':
                    continue
                try:
                    data = json.loads(raw)
                except json.decoder.JSONDecodeError:
                    print(f"JSON Error: {raw}")
                    continue
                # self.drive_manual(data)
                self.gripperHandler.target_close_offset = data["modClosePosition"]
                self.last_data = data

    def drive_manual (self, data):
        if data["type"] == "ControlUpdate":
            try:
                if data["leftGripperClosed"]:
                    self.gripperHandler.close_left()
                else:
                    self.gripperHandler.open_left()

                if data["rightGripperClosed"]:
                    self.gripperHandler.close_right()
                else:
                    self.gripperHandler.open_right()

                self.target_gripper_pan += (-0.5 * data["pan"] * data["modPanSpeed"])
                self.target_gripper_tilt += (-0.4 * data["tilt"] * data["modTiltSpeed"])

                self.target_gripper_pan = max(0.5 * math.pi, min(1.5 * math.pi, self.target_gripper_pan))
                self.target_gripper_tilt = max(0.85 * math.pi, min(1.5 * math.pi, self.target_gripper_tilt)) 
                self.gripperHandler.set_gripper_pan(self.target_gripper_pan)
                self.gripperHandler.set_gripper_tilt(self.target_gripper_tilt)
                self.motors.move(data["x"] * data["modMotorSpeed"], data["y"] * data["modMotorSpeed"], -data["rotation"] * data["modRotationSpeed"])
            except gripper_handler.OscarBotArmException as exc:
                print(exc)


if __name__ == "__main__":
    #TODO: Let's just print the data
    pass

