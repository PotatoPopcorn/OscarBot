import math
import time
import traceback

from datetime import datetime

import numpy as np

import gripper_handler
import motor_handler
import oscar_kinematics
import pid_controller
import serial_handler
import tracker_handler
import tracker_kinematics
import unity_handler

try:
    serial_handle = serial_handler.SerialHandler()
except serial_handler.SerialSetupException as exc:
    print(exc)
    exit()

input("Press Enter to start movements\n")

dynamixel = serial_handle.get_dynamixel_path()

gripper = gripper_handler.GripperHandler(dynamixel)

gripper.enable_gripper()

motors = motor_handler.MotorHandler(serial_handle)

unity = unity_handler.UnityHandler(gripper, motors)

track = tracker_handler.TrackerHandler()

kine = tracker_kinematics.TrackerKinematics()

pid_x = pid_controller.PIDControl(0.0025, 0.0007, 0)#, static_factor = 500000, static_ki = 50000, static_limit=200)
pid_y = pid_controller.PIDControl(0.0025, 0.0007, 0)#, static_factor = 500000, static_ki = 50000, static_limit=200)
pid_rot = pid_controller.PIDControl(0.1, 0.05, 0, static_factor = 0.1)# (0.5, 0.2, 0) #, static_factor = 0.5)

stop_counter = 0

def auto_mode():
    
    rot = oscar_kinematics.get_difference_in_euler_angles(
       track.get_robot_track()['rotation_euler']['Z'],
       0
       )



    kine.setRootPositionAndRotation([track.get_robot_track()['location']['X'], track.get_robot_track()['location']['Y'], track.get_robot_track()['location']['Z']], track.get_robot_track()['rotation_matrix'])
    offset = kine.getLocalPosition([0, 0, 0])
    
    off_x = pid_x.update(offset[0], 0)
    off_y = pid_y.update(offset[1], 0)

    print("RECORD:", rot, offset, np.sqrt(offset[0]*offset[0]+offset[1]*offset[1]), datetime.now())

    off_rot = pid_rot.update(rot, 0)
    # print(rot, cont)
    motors.move(off_x, off_y, off_rot)

#    if np.abs(pid_x.speed) > 0.0001 or np.abs(pid_y.speed) > 0.0001:
#        print("DIST:", np.sqrt((offset[0]) ** 2 + (offset[1]) ** 2), "SPEED X:", pid_x.speed, "Y:", pid_y.speed)
#        gripper.set_gripper_pan(np.pi)
#        if np.sqrt((offset[0]) ** 2 + (offset[1]) ** 2) < 15 and np.abs(rot) < 0.15:
#            gripper.set_gripper_tilt(7 * np.pi / 6)
#            stop_counter += 1
#            if stop_counter > 25:
#                gripper.close_left()
#            if stop_counter > 50:
#                break

#        else:
#            gripper.set_gripper_tilt(np.pi)
#            stop_counter = 0
#            gripper.open_left()

try:
    while True:
        if "mode" in unity.last_data:
            if unity.last_data["mode"] == 1:
                pid_x.reset()
                pid_y.reset()
                pid_rot.reset()
                unity.drive_manual(unity.last_data)
            elif unity.last_data["mode"] == 2:
                auto_mode()
                # print("Auto Mode")
        else:
            # print("Inactive")
            motors.move(0, 0, 0)
        #print(f"31: {gripper._get_link_current(31)}, 34: {gripper._get_link_current(34)}")
except Exception as exc:
    traceback.print_exc()
    motors.move(0, 0, 0)


motors.move(0, 0, 0)

gripper.set_gripper_tilt(np.pi / 2)

time.sleep(5)

gripper.disable_gripper()

# left_arduino.write(bytes("IDU05FFFF1000\r\n", "ASCII"))
# right_arduino.write(bytes("IDU06FFFF1000\r\n", "ASCII"))
