"""
****************************************
Created on Tue Jun 21 12:45:26 2021
@authors: Victoire Destombes, Andrea Bassi, Emma Martinelli. Politecnico di Milano

"""

from pipython import GCSDevice, pitools
import time
from numpy import sign
import warnings


class PI_VC_Device(object):
    '''
    Scopefoundry compatible class to run Physics Instruments motors
    '''
    # add your device and the maximum speed otherwise the maximum speed is set to 2.5
    VELOCITY = {'M-403.4DG': 2.5,  # SPIM translator stage
                'V-524.1AA': 250.0,  # voice coil
                'L-402.10SD': 5.0,  # linear stage
                }

    def __init__(self, serial='0000000000', axis='1'):
        self.serial = serial
        self.axis = axis
        self.pi_device = GCSDevice()
        self.pi_device.ConnectUSB(serial)

        self.set_servo(mode=True)
        self.gotoRefSwitch()
        self.pi_device.RON(self.axis, True)
        # self.set_home()    already done in the gotoRefSwitch
        self.direction = 1  # to be used for backslash correction (sign of the direction, +1 or -1)
        self.name = self.pi_device.qCST()[axis]

    def get_info(self):
        # info  = f'{self.pi_device.qIDN()}'
        info = self.name
        return info

    def get_mode(self):
        referencemode = self.pi_device.qRON(self.axis)
        return referencemode

    def get_servo(self):
        servomode = self.pi_device.qSVO(self.axis)[self.axis]
        return servomode

    def set_servo(self, mode=False):
        self.pi_device.SVO(self.axis, mode)
        # print(f'Servo set to {mode}')

    def move_absolute(self, desired_pos, correct_backslash=False):
        rel_pos = self.home + desired_pos
        rangemin = self.pi_device.qTMN()[self.axis]
        rangemax = self.pi_device.qTMX()[self.axis]
        pos = min(rangemax, max(rel_pos, rangemin))
        if rel_pos < rangemin:
            warnings.warn(f"Displacement {pos} smaller than {rangemin}", UserWarning)
        elif rel_pos > rangemax:
            warnings.warn(f"Displacement {pos} bigger than {rangemax}", UserWarning)
        displacement = rel_pos - self.get_position()
        if correct_backslash:
            self.correct_backslash(displacement)
        self.pi_device.MOV(self.axis, pos)
        self.direction = sign(displacement)

    def move_relative(self, desired_disp, correct_backslash=False):
        disp = desired_disp * 0.001

        rangemin = self.pi_device.qTMN()[self.axis]
        rangemax = self.pi_device.qTMX()[self.axis]
        pos = self.get_position() + disp
        if pos < rangemin:
            warnings.warn(f"Displacement {pos} smaller than {rangemin}", UserWarning)
            disp = 0
        elif pos > rangemax:
            warnings.warn(f"Displacement {pos} bigger than {rangemax}", UserWarning)
            disp = 0

        if correct_backslash:
            self.correct_backslash(disp)
        self.pi_device.MVR(self.axis, disp)
        self.direction = sign(disp)

    def get_position(self):
        self.wait_on_target()
        position = self.pi_device.qPOS(self.axis)[self.axis] - self.home
        print('real position: ', self.pi_device.qPOS(self.axis)[self.axis])
        return position

    def set_home(self):
        self.home = self.pi_device.qPOS(self.axis)[self.axis]
        print('home position: ', self.home)

    def get_home(self):
        home = self.pi_device.qDFH(self.axis)[self.axis]
        return home

    def go_home(self):
        pitools.moveandwait(self.pi_device, self.axis, self.home)

    def stop(self):
        self.pi_device.HLT(self.axis)

    def gotoRefSwitch(self):
        self.pi_device.FRF(self.axis)
        self.wait_on_target()
        self.set_home()

    def wait_on_target(self):
        if not self.pi_device.qONT(self.axis)[self.axis]:
            time.sleep(0.05)
            self.wait_on_target()
        # else:
        #     print('On target')

    def correct_backslash(self, displacement):
        new_direction = sign(displacement)

        if new_direction != self.direction:
            delta = 0.05 * new_direction
            self.pi_device.MVR(self.axis, delta)
            self.pi_device.MVR(self.axis, -delta)

    def get_velocity(self):
        vel = self.pi_device.qVEL(self.axis)[self.axis]
        return vel

    def set_velocity(self, desired_velocity):
        vmin = 0.000001
        vmax = 2.5

        if self.name in self.VELOCITY.keys():
            vmax = self.VELOCITY[self.name]

        velocity = min(vmax, max(desired_velocity, vmin))
        self.pi_device.VEL(self.axis, velocity)

    def before_trigger(self):
        self.pi_device.DIO(1,1)
        time.sleep(3)
        self.pi_device.DIO(1,0)

    def trigger(self, trigger_step, trigger_start, trigger_stop):
        correction = 0.1
        for i in range(1, 4):
            self.pi_device.TRO(i, 0)

        # trigger output conditions configuration
        self.pi_device.CTO(1, 2, 1)
        self.pi_device.CTO(1, 3, 0)
        self.pi_device.CTO(1, 1, trigger_step)
        self.pi_device.CTO(1, 8, trigger_start - correction)
        self.pi_device.CTO(1, 9, trigger_stop + correction)

        # enable the condition for trigger output
        self.pi_device.TRO(1, 1)

        self.pi_device.MOV(self.axis, trigger_stop + correction)

    def trigger_start(self, trigger_stop, trigger_start):
        # self.pi_device.MOV(self.axis, trigger_start)
        for i in range(1, 4):
            self.pi_device.TRO(i, 0)

        # trigger output conditions configuration
        self.pi_device.CTO(1, 2, 1)
        self.pi_device.CTO(1, 3, 0)
        self.pi_device.CTO(1, 8, trigger_start)

        # enable the condition for trigger output
        self.pi_device.TRO(1, 1)

        self.pi_device.MOV(self.axis, trigger_stop)

    def close(self):
        # self.stop()
        self.pi_device.close()

        # trigger external start

    def PI_velocity(self, t_exp, step):
        vel = step / t_exp
        print('velocity: ', vel)
        if vel < 0.000001:
            print('slow')
            vel = 0.000001
        if vel > 2.5:
            print('too fast, use trigger ext')
            vel = 2.5
        return vel


if __name__ == "__main__":

    # If you want to test the device class directly write here the serial number of your device
    motor = PI_VC_Device('0185500006')
    try:

        print('Device:', motor.pi_device.devname)
        print('Initial position:', motor.get_position())
        print('Velocity:', motor.get_velocity())
        print('Mode:', motor.get_mode())
        motor.move_relative(0.5)
        motor.wait_on_target()
        print('Final position:', motor.get_position())
        motor.move_absolute(2.0)
        motor.wait_on_target()
        print('Final position:', motor.get_position())

    finally:
        motor.close()

























