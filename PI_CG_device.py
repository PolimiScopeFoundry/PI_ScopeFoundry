"""
****************************************
Created on Tue Jun 21 12:45:26 2021
@authors: Victoire Destombes, Andrea Bassi. Politecnico di Milano

"""

from PI_ScopeFoundry.PIPython.pipython import GCSDevice
import time
from numpy import sign

class PI_CG_Device(object):
    '''
    Scopefoundry compatible class to run a FLIR camera with spinnaker software
    For Pointgrey grasshopper, the bit depth is 16bit or 8bit, specified in the PixelFormat attribute, 
    simple_pyspin is not compatible with 12bit readout. 
    '''
    
    VELOCITY = {'M-405.CG_VEL0.7MMS': 0.7, 
              }
    
    
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
        displacement = desired_pos - self.get_position()
        if correct_backslash:
            self.correct_backslash(displacement)
        self.pi_device.MOV(self.axis, pos)
        self.direction = sign(displacement)
        
    def move_relative(self, displacement, correct_backslash = False):
        if correct_backslash:
            self.correct_backslash(displacement)
        self.pi_device.MVR(self.axis, displacement)
        self.direction = sign(displacement)
        
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
    
        
    
        

        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        