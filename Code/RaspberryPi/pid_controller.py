from datetime import datetime   
import numpy as np

# SOURCE: https://softinery.com/blog/implementation-of-pid-controller-in-python/

class PIDControl:
    def __init__(self, kp, ki, kd, static_factor = 0.0, static_limit = 1, static_ki=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_time = datetime.now()
        self.prev_error = 0
        self.integral = 0
        self.static_factor = static_factor
        self.static_limit = static_limit
        self.static_ki = static_ki
        self.speed = 0
        self.prev_result = 0

    def update(self, current, goal):
        now_time = datetime.now()
        e = current - goal
        #if e == self.prev_error:
        #    return self.prev_result

        proportional = self.kp * e
        self.integral += self.ki*e*((now_time - self.prev_time).total_seconds())
        differential = self.kd * (e - self.prev_error) / ((now_time - self.prev_time).total_seconds())

        self.speed = (e - self.prev_error) / ((now_time - self.prev_time).total_seconds())

        static_correction = (self.static_factor * e) + (self.static_ki * self.integral) if (np.abs(self.speed) < self.static_limit and np.abs(self.speed) > 0.0001) else 0

        #if np.abs(speed) > 0.0001:
            #print(speed)

        result = proportional + self.integral + differential + static_correction

        self.prev_error = e
        self.prev_time = now_time
        self.prev_result = result

        return result

    def reset(self):
        self.integral = 0
        self.prev_error = 0
