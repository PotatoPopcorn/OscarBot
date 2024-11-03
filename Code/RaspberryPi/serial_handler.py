from enum import Enum
import os

import serial

MIN_SUPPORTED_VERSION = (2,0,0)

class SerialType(Enum):
    DEVICE_UNKNOWN = 0
    SIDE_UNKNOWN = 1
    SIDE_LEFT = 3
    SIDE_RIGHT = 5

class SerialSetupException(Exception):
    pass

class DeviceNotConnectedException(Exception):
    pass

class SerialHandler:
    def __init__(self):
        # Define all of the devices
        self.left_arduino = None
        self.right_arduino = None
        self.dynamixel_driver = None
        self.added_devices = list()

        # Create a empty list to store all of the devices that may be connected to the Pi
        potential_devices = list()

        # Iterate over all of the devices in /dev
        for path in os.listdir('/dev/'):
            # Arduino devices connect as /dev/ttyACMX, so we can ignore anything that isn't relevant
            if not path.startswith('ttyACM'):
                continue
            potential_devices.append(self._process_init_data(f'/dev/{path}'))

        # There must only be 2 or 3 devices connected to the system, if there are 2, then they have to be the left and
        # right controller, the third must be the dynamixel controller. If any other number is connected, then we have
        # a problem
        if len(potential_devices) not in [2, 3]:
            raise SerialSetupException(f"Invalid number of serial devices: {len(potential_devices)}, " + 
                    f"Please make sure that only and all of the OscarSerial devices are connected")

        unknown_side_device = None # Create a variable to store a device which is not reporting its side

        for (dev, path, side, version) in potential_devices:
            #TODO: Add handling for unsupported versions
            
            # If side is reporting correctly, check if it is the only device in there and if not assign it
            if side == SerialType.SIDE_LEFT:
                if self.left_arduino is not None:
                    raise SerialSetupException("Multiple Left Controllers Dectected, Confirm Side Detection Circuit")
                else:
                    self.left_arduino = (dev, path, version)
                    self.added_devices.append(path)
            elif side == SerialType.SIDE_RIGHT:
                if self.right_arduino is not None:
                    raise SerialSetupException("Multiple Right Controllers Dectected, Confirm Side Detection Circuit")
                else:
                    self.right_arduino = (dev, path, version)
                    self.added_devices.append(path)

            # Store the unknown device into the variable, if there is more then one, then we have no way to determine which
            # is which so we want to raise an excption
            elif side == SerialType.SIDE_UNKNOWN:
                print(f"WARNING, Device with unknown side: {path}")
                if unknown_side_device is not None:
                    raise SerialSetupException("Multiple Controllers Detected with Unknown Side, Confirm Side Detection Circuits")
                else:
                    unknown_side_device = (dev, path, version)

            # If a device is not responding with the started format, then it is likely the dynamixel controller, therefore we can 
            # assign it if there is only one. 
            elif side == SerialType.DEVICE_UNKNOWN:

                # If there are only two devices, we cannot have a dynamixel controller connected yet.
                if len(potential_devices) == 2:
                    raise SerialSetupException("Unknown device with only two connected, confirm all motor controllers are connected" + 
                            "and all devices have the correct code flashed onto them")
                elif self.dynamixel_driver is not None:
                    raise SerialSetupException("Multiple unknown devices are connected, please make sure that only the correct devices are" + 
                            "connected and that all devices have their code put onto them")
                else:
                    self.dynamixel_driver = (dev, path, version)
            # If we get there then we have hit a scenario where there is a Serial Type that is not covered by one of the previous cases and we
            # have messed up
            else:
                raise SerialSetupException(f"Unknwon SerialType Value specified: {side}, Check Code")

        # Assign the unknown arduino to the side which has not been assigned. If both sides have been assigned, then we may have 3 arduinos 
        # is a problem
        if unknown_side_device is None:
            pass # Ignore these checks if there is no unknown device
        elif self.left_arduino is None:
            print(f"Assigning {unknown_side_device[1]} to the left side")
            self.left_arduino = unknown_side_device
            self.added_devices.append(unknown_side_device[1])
        elif self.right_arduino is None:
            print(f"Assigning {unknown_side_device[1]} to the right side")
            self.right_arduino = unknown_side_device
            self.added_devices.append(unknown_side_device[1])
        else:
            raise SerialSetupException(f"Unable to assign unknown side device: {unknown_side_device[1]}")

        # This check should never fail, it means that after all of that previous checking, we have somehow ended up with one of the drivers still missing.
        if self.left_arduino is None or self.right_arduino is None:
            raise SerialSetupException(f"Either Left or Right Arduino is unassigned, check connections and code: \nLEFT: {self.left_arduino}\nRIGHT: {self.right_arduino}")
 

    def _process_init_data(self, path):
        dev = serial.Serial(path, 115200, timeout=10) # Connect to the device
        start = dev.readline().decode('ASCII') 
        if not start.startswith('Started'): # See if we have the startted packet, if not then we don't know what the device is
            return dev, path, SerialType.DEVICE_UNKNOWN, (None, None, None) # The Nones will definitely not come back to byte us later
        dev.write(bytes("INI\n", "ASCII"))
        iniinfo = dev.readline()
        version = (int(iniinfo[3]), int(iniinfo[4]), int(iniinfo[5])) 
        side = SerialType.SIDE_LEFT if iniinfo[6] == 76 else (SerialType.SIDE_RIGHT if iniinfo[6] == 82 else SerialType.SIDE_UNKNOWN) # Determine which side it is from the INI data
        return dev, path, side, version

    def get_left_serial(self):
        if self.left_arduino is None:
            raise SerialSetupException("Left Arduino was set to none, check code")
        return self.left_arduino[0]

    def get_right_serial(self):
        if self.right_arduino is None:
            raise SerialSetupException("Left Arduino was set to none, check code")
        return self.right_arduino[0]
           
    def get_dynamixel_serial(self):
        if self.dynamixel_driver is not None:
            return self.dynamixel_driver[0]
        for dev in os.listdir('/dev/'):
            if (not dev.startswith('ttyACM')) or f'/dev/{dev}' in self.added_devices:
                continue
            #TODO Check I'm not missing anything here
            return serial.Serial(f'/dev/{dev}', 115200, timeout=10)
        raise DeviceNotConnectedException("Could not find any other connected devices")

    def get_dynamixel_path(self):
        if self.dynamixel_driver is not None:
            return self.dynamixel_driver[1]
        for dev in os.listdir('/dev/'):
            if (not dev.startswith('ttyACM')) or f'/dev/{dev}' in self.added_devices:
                continue
            #TODO Check I'm not missing anything here
            return f'/dev/{dev}'
        raise DeviceNotConnectedException("Could not find any other connected devices")
