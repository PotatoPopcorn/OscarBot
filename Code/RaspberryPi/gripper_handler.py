import math
import time

import dynamixel_sdk

class OscarBotArmException(Exception):
    pass

class GripperHandler:
    def __init__(self, device_name:str):
        self.active_dev_ids = [31, 32, 33, 34, 40, 42]
        self.PROTOCOL_VERSION = 2.0
        self.BAUDRATE = 57600
        self.DEVICENAME = device_name

        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_GOAL_POSITION = 116
        self.ADDR_PRESENT_CURRENT = 126
        self.ADDR_PRESENT_POSITION = 132
        self.ADDR_LED_ENABLE = 65
        self.DXL_MINIMUM_POSITION_VALUE = 0
        self.DXL_MAXIMUM_POSITION_VALUE = 4095

        self.TORQUE_ENABLE = 1
        self.TORQUE_DISABLE = 0
        self.DXL_MOVING_STATUS_THRESHOLD = 20

        self.target_close_offset = 0.05

        #self.is_left_closed = False
        #self.is_right_closed = False

        self.portHandler = dynamixel_sdk.PortHandler(self.DEVICENAME)
        self.packetHandler = dynamixel_sdk.PacketHandler(self.PROTOCOL_VERSION)
        if not self.portHandler.openPort():
            raise OscarBotArmException("Could not open port")

        if not self.portHandler.setBaudRate(self.BAUDRATE):
            raise OscarBotArmException("Could not change baudrate")

    def _test_ping(self, dev_id:int):
        dxl_model_number, dxl_comm_result, dxl_error = self.packetHandler.ping(self.portHandler, dev_id)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            raise OscarBotArmException(f"Failed to ping device with ID: {dev_id} - "
                                    f"{self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise OscarBotArmException(f"Failed to ping device with ID: {dev_id} - "
                                    f"{self.packetHandler.getRxPacketError(dxl_error)}")

    def _set_led(self, dev_id:int, state:bool):
        led_mode = self.TORQUE_ENABLE if state else self.TORQUE_DISABLE
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dev_id, self.ADDR_LED_ENABLE, led_mode)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            raise OscarBotArmException(f"Failed to set torque of device with ID: {dev_id} - "
                                    f"{self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise OscarBotArmException(f"Failed to set torque of device with ID: {dev_id} - "
                                    f"{self.packetHandler.getRxPacketError(dxl_error)}")

    def _set_enable_torque(self, dev_id:int, state:bool):
        torque_mode = self.TORQUE_ENABLE if state else self.TORQUE_DISABLE
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dev_id, self.ADDR_TORQUE_ENABLE, torque_mode)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            raise OscarBotArmException(f"Failed to set torque of device with ID: {dev} - "
                                   f"{self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise OscarBotArmException(f"Failed to set torque of device with ID: {dev} - "
                                   f"{self.packetHandler.getRxPacketError(dxl_error)}")

    def _set_link_angle(self, link_id: int, angle: float):
        angle = int(angle * self.DXL_MAXIMUM_POSITION_VALUE / (2 * math.pi))
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, link_id, self.ADDR_GOAL_POSITION, angle)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            raise OscarBotArmException(f"Failed to set angle of device with ID: {link_id} - "
                                       f"{self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise OscarBotArmException(f"Failed to set angle of device with ID: {link_id} - "
                                       f"{self.packetHandler.getRxPacketError(dxl_error)}")

    def _get_link_angle(self, link_id: int):
        dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(self.portHandler, link_id, self.ADDR_PRESENT_POSITION)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            raise OscarBotArmException(
                f"Failed to get angle of device with ID: {link_id} - {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise OscarBotArmException(
                f"Failed to get angle of device with ID: {link_id} - {self.packetHandler.getRxPacketError(dxl_error)}")
        angle = dxl_present_position * (2 * math.pi) / self.DXL_MAXIMUM_POSITION_VALUE
        return angle

    def _get_link_current(self, link_id: int):
        dxl_present_current, dxl_comm_result, dxl_error = self.packetHandler.read2ByteTxRx(self.portHandler, link_id, self.ADDR_PRESENT_CURRENT)
        if dxl_comm_result != dynamixel_sdk.COMM_SUCCESS:
            raise OscarBotArmException(
                f"Failed to get current of device with ID: {link_id} - {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise OscarBotArmException(
                f"Failed to get current of device with ID: {link_id} - {self.packetHandler.getRxPacketError(dxl_error)}")
        print(dxl_present_current)
        out_current = dxl_present_current if dxl_present_current < 2 ** 15 else dxl_present_current - 2 ** 16 
        return out_current

    def enable_gripper(self):
        for dev_id in self.active_dev_ids:
            self._set_led(dev_id, True)
            self._set_enable_torque(dev_id, True)
        self._set_link_angle(32, 1.25 * math.pi)
        self._set_link_angle(33, 0.75 * math.pi)
    
    def disable_gripper(self):
        for dev_id in self.active_dev_ids:
            self._set_enable_torque(dev_id, False)
            self._set_led(dev_id, False)

    def open_left(self):
        self._set_link_angle(31, math.pi)
    
    def close_left(self):
        # TODO: if this isn't sufficient, figure out how to read current values
        self._set_link_angle(31, (0.75 + self.target_close_offset) * math.pi)

    def open_right(self):
        self._set_link_angle(34, math.pi)
        #self.is_right_closed = False

    def close_right(self):
        #if self.is_right_closed:
        #    return
        # TODO: if this isn't sufficient, figure out how to read current values
        self._set_link_angle(34, (1.25 - self.target_close_offset) * math.pi)
        #link_angle = 1.30 * math.pi
        #if self._get_link_current(34) < self.target_close_current:
        #    while self._get_link_current(34) < self.target_close_current:
        #        time.sleep(0.05)
        #        link_angle += 0.01
        #        self._set_link_angle(34, link_angle)
        #elif self._get_link_current(34) > self.target_close_current + 150:
        #    while self._get_link_current(34) > self.target_close_current + 150:
        #        time.sleep(0.01)
        #        link_angle -= 0.01
        #        self._set_link_angle(34, link_angle)
        #self.is_right_closed = True



    def set_gripper_pan(self, angle:float):
        angle = max(0.5 * math.pi, min(1.5 * math.pi, angle))
        self._set_link_angle(40, angle)

    def get_gripper_pan(self):
        return self._get_link_angle(40)

    def set_gripper_tilt(self, angle:float):
        angle = max(0.85 * math.pi, min(1.5 * math.pi, angle))
        self._set_link_angle(42, angle)

    def get_gripper_tilt(self):
        return self._get_link_angle(42)

    def __del__(self):
        self.disable_gripper()
        self.portHandler.closePort()
