import numpy as np

import oscar_kinematics 
import serial_handler

WHEEL_CONFIG = {
    'nw': {
        'serial': 2,
        'shift': 2,
        'dir': False
    },
    'ne': {
        'serial': 1,
        'shift': 0,
        'dir': True
    },
    'se': {
        'serial': 1,
        'shift': 2,
        'dir': False
    },
    'sw': {
        'serial': 2,
        'shift': 0,
        'dir': False
    }
}

class MotorHandler:
    def __init__(self, serial: serial_handler.SerialHandler):
        self.left = serial.get_left_serial() 
        self.right = serial.get_right_serial()

    def _decode_wheel_information(self, dir, settings):
        r2 = np.min([255, np.floor(dir*255)])
        if dir < 0.001 and dir > -0.001:
            return 0, 0
        elif dir < 0:
            r1 = 1 if settings["dir"] else 2
            r2 *= -1
        else:
            r1 = 2 if settings["dir"] else 1

        r1 = r1 << settings["shift"]

        return r1, int(r2)

    def move(self, x1:float, x2:float, rot:float):
        nw, ne, se, sw = oscar_kinematics.wheel_movment_kinematics(x1, x2, rot)
        nw1, nw2 = self._decode_wheel_information(nw, WHEEL_CONFIG['nw'])
        ne1, ne2 = self._decode_wheel_information(ne, WHEEL_CONFIG['ne'])
        se1, se2 = self._decode_wheel_information(se, WHEEL_CONFIG['se'])
        sw1, sw2 = self._decode_wheel_information(sw, WHEEL_CONFIG['sw'])

        wdir = nw1 + sw1
        edir = ne1 + se1

        frame1 = bytearray(b'CDU')
        frame2 = bytearray(b'CDU')

        frame1.extend(bytes(f"{edir:02x}", "ascii"))
        frame2.extend(bytes(f"{wdir:02x}", "ascii"))

        frame1.extend(bytes(f"{ne2:02x}", "ascii"))
        frame1.extend(bytes(f"{se2:02x}\n", "ascii"))
        frame2.extend(bytes(f"{sw2:02x}", "ascii"))
        frame2.extend(bytes(f"{nw2:02x}\n", "ascii"))

        self.right.write(bytes(frame1))
        self.left.write(bytes(frame2))        

    def stop(self):
        self.left.write(b"HAL\n")
        self.right.write(b"HAL\n")
