"""
****************************************
Created on Tue Jun 21 12:45:26 2021
@authors: Victoire Destombes, Andrea Bassi, Emma Martinelli. Politecnico di Milano

"""

from pipython import GCSDevice, pitools
import time
from numpy import sign
import warnings

class PI_CG_Device(object):
    '''
    Scopefoundry compatible class to run Physics Instruments motors
    '''
    
    # VELOCITY = {'M-405.CG_VEL0.7MMS': 0.7,
    #           }

    def __init__(self, serial = '0135500826', axis = '1'):
        self.serial = serial
        self.axis = axis
        self.pi_device = GCSDevice()                       
        self.pi_device.ConnectUSB (serial)

        self.set_servo(mode = True)
        self.gotoRefSwitch()
        self.pi_device.RON(self.axis, True) 
        self.set_home()
        self.direction = 1 # to be used for backslash correction (sign of the direction, +1 or -1)
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
   
    def set_servo(self, mode = False): 
        self.pi_device.SVO(self.axis, mode)
        # print(f'Servo set to {mode}')

    def move_absolute(self, desired_pos, correct_backslash = False):
        rangemin = self.pi_device.qTMN()[self.axis]
        rangemax = self.pi_device.qTMX()[self.axis]
        pos = min(rangemax, max(desired_pos, rangemin))
        if desired_pos < rangemin:
            warnings.warn(f"Displacement {pos} smaller than {rangemin}", UserWarning)
        elif desired_pos > rangemax:
            warnings.warn(f"Displacement {pos} bigger than {rangemax}", UserWarning)
        displacement = desired_pos - self.get_position()
        if correct_backslash:
            self.correct_backslash(displacement)
        self.pi_device.MOV(self.axis, pos)
        self.direction = sign(displacement)
        
    def move_relative(self, desired_disp, correct_backslash = False):
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
        position = self.pi_device.qPOS(self.axis)[self.axis]    
        return position
    
    def set_home(self):
        self.pi_device.DFH(self.axis)
        
    def get_home(self):    
        home = self.pi_device.qDFH(self.axis)[self.axis]
        return home
    
    def go_home(self):
        self.pi_device.GOH(self.axis)
                
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
        else:
            print('On target')
        
    
    def correct_backslash(self, displacement):
        new_direction = sign(displacement)
        
        if  new_direction != self.direction:
            delta = 0.05*new_direction
            self.pi_device.MVR(self.axis, delta)   
            self.pi_device.MVR(self.axis, -delta)   
        
    
    def get_velocity(self):
        vel = self.pi_device.qVEL(self.axis)[self.axis]
        return vel
        
    def set_velocity(self, desired_velocity):
        
        vmin = 0.01
        vmax = 15
        
        if self.name in self.VELOCITY.keys():
            vmax = self.VELOCITY[self.name] 
            
        velocity = min(vmax, max(desired_velocity, vmin)) 
        self.pi_device.VEL(self.axis, velocity)

    def trigger(self, trigger_step, trigger_stop):
        for i in range(1, 4):
            self.pi_device.TRO(i, 0)

        # trigger output conditions configuration
        self.pi_device.CTO(1, 2, 1)
        self.pi_device.CTO(1, 3, 0)
        self.pi_device.CTO(1, 1, trigger_step)
        self.pi_device.CTO(4, 8, 0)
        self.pi_device.CTO(4, 9, 0)

        # enable the condition for trigger output
        self.pi_device.TRO(1, 1)

        self.pi_device.MOV(self.axis, trigger_stop)
        
    def close(self):
        #self.stop()
        self.pi_device.close()
        
        
if __name__ == "__main__":
    
    motor = PI_CG_Device()
    try: 
        
        print('Position:', motor.get_position())
        motor.move_relative(0.5)
        #motor.gotoRefSwitch()
        # print('Home:', motor.get_home())
        print('mode:', motor.get_mode())
        
        # motor.set_velocity(0.7)
        
        motor.stop()
        #motor.move_relative(-0.1, True)
        
        #motor.wait_on_target()
        #motor.gotoRefSwitch()
        print('Position:', motor.get_position())
        print(motor.pi_device.devname)
        
        # print('Position:', motor.get_position())
    
    finally:
        motor.close()
    
        
    
        

        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        