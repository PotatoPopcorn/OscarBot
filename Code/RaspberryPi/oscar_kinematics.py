import unittest

import numpy as np

# RIP My Sanity

_COS45 = 0.707106769084930419921875

def wheel_movment_kinematics(x1:float, x2:float, r:float) -> tuple:
    mag = np.linalg.norm([x1, x2])
    if mag > 1:
        x1 /= mag
        x2 /= mag

    nw = x2 * _COS45 + x1*_COS45 - r #=$B$2*COS(PI()/4)+$A$2*COS(PI()/4)-$C$2
    ne = x2 * _COS45 - x1*_COS45 + r #=$B$2*SIN(PI()/4)-$A$2*SIN(PI()/4)+$C$2
    se = x2 * _COS45 + x1*_COS45 + r #=$B$2*COS(PI()/4)+$A$2*COS(PI()/4)+$C$2
    sw = x2 * _COS45 - x1*_COS45 - r #=$B$2*SIN(PI()/4)-$A$2*SIN(PI()/4)-$C$2
    return nw, ne, se, sw

def get_difference_in_euler_angles(theta_current, theta_goal):
    option1 = theta_goal - theta_current
    option2 = (theta_goal + 2 * np.pi) - theta_current
    option3 = (theta_goal - 2 * np.pi) - theta_current

    if np.abs(option1) < np.abs(option2) and np.abs(option1) < np.abs(option3):
        return option1
    elif np.abs(option2) < np.abs(option3):
        return option2
    else:
        return option3


class _KinematicTests(unittest.TestCase):
    # TODO: magnitude tests

    def test_basic_angle_1(self):
        self.assertAlmostEqual(get_difference_in_euler_angles(np.pi, np.pi/2), -np.pi/2)

    def test_basic_angle_2(self):
        self.assertAlmostEqual(get_difference_in_euler_angles(np.pi/4, np.pi/2), np.pi/4)

    def test_basic_angle_3(self):
        self.assertAlmostEqual(get_difference_in_euler_angles(np.pi/2, 3*np.pi/3), np.pi/2)

    def test_invert_angle_1(self):
        self.assertAlmostEqual(get_difference_in_euler_angles(7*np.pi/4, np.pi/4), np.pi/2)

    def test_invert_angle_2(self):
        self.assertAlmostEqual(get_difference_in_euler_angles(np.pi/4, 7*np.pi/4), -np.pi/2)

    def test_north(self):
        nw, ne, se, sw = wheel_movment_kinematics(0, 1, 0)
        self.assertAlmostEqual(nw, _COS45)
        self.assertAlmostEqual(ne, _COS45)
        self.assertAlmostEqual(se, _COS45)
        self.assertAlmostEqual(sw, _COS45)

    def test_south(self):
        nw, ne, se, sw = wheel_movment_kinematics(0, -1, 0)
        self.assertAlmostEqual(nw, -_COS45)
        self.assertAlmostEqual(ne, -_COS45)
        self.assertAlmostEqual(se, -_COS45)
        self.assertAlmostEqual(sw, -_COS45)

    def test_east(self):
        nw, ne, se, sw = wheel_movment_kinematics(1, 0, 0)
        self.assertAlmostEqual(nw, _COS45)
        self.assertAlmostEqual(ne, -_COS45)
        self.assertAlmostEqual(se, _COS45)
        self.assertAlmostEqual(sw, -_COS45)

    def test_west(self):
        nw, ne, se, sw = wheel_movment_kinematics(-1, 0, 0)
        self.assertAlmostEqual(nw, -_COS45)
        self.assertAlmostEqual(ne, _COS45)
        self.assertAlmostEqual(se, -_COS45)
        self.assertAlmostEqual(sw, _COS45)

    def test_northeast(self):
        nw, ne, se, sw = wheel_movment_kinematics(_COS45, _COS45, 0)
        self.assertAlmostEqual(nw, 1)
        self.assertAlmostEqual(ne, 0)
        self.assertAlmostEqual(se, 1)
        self.assertAlmostEqual(sw, 0)
    def test_southeast(self):
        nw, ne, se, sw = wheel_movment_kinematics(_COS45, -_COS45, 0)
        self.assertAlmostEqual(nw, 0)
        self.assertAlmostEqual(ne, -1)
        self.assertAlmostEqual(se, 0)
        self.assertAlmostEqual(sw, -1)
    def test_southwest(self):
        nw, ne, se, sw = wheel_movment_kinematics(-_COS45, -_COS45, 0)
        self.assertAlmostEqual(nw, -1)
        self.assertAlmostEqual(ne, 0)
        self.assertAlmostEqual(se, -1)
        self.assertAlmostEqual(sw, 0)
    def test_northwest(self):
        nw, ne, se, sw = wheel_movment_kinematics(-_COS45, _COS45, 0)
        self.assertAlmostEqual(nw, 0)
        self.assertAlmostEqual(ne, 1)
        self.assertAlmostEqual(se, 0)
        self.assertAlmostEqual(sw, 1)

    def test_zero(self):
        nw, ne, se, sw = wheel_movment_kinematics(0, 0, 0)
        self.assertAlmostEqual(nw, 0)
        self.assertAlmostEqual(ne, 0)
        self.assertAlmostEqual(se, 0)
        self.assertAlmostEqual(sw, 0)

    def test_cw(self):
        nw, ne, se, sw = wheel_movment_kinematics(0, 0, -1)
        self.assertAlmostEqual(nw, 1)
        self.assertAlmostEqual(ne, -1)
        self.assertAlmostEqual(se, -1)
        self.assertAlmostEqual(sw, 1)

    def test_ccw(self):
        nw, ne, se, sw = wheel_movment_kinematics(0, 0, 1)
        self.assertAlmostEqual(nw, -1)
        self.assertAlmostEqual(ne, 1)
        self.assertAlmostEqual(se, 1)
        self.assertAlmostEqual(sw, -1)


if __name__ == '__main__':
    unittest.main()
