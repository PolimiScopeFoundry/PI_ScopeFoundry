"""
****************************************
Created on Tue Jun 21 12:45:26 2021
@authors: Victoire Destombes, Andrea Bassi. Politecnico di Milano

"""

from PI_ScopeFoundry.PIPython.pipython import GCSDevice
import time

class PI_CG_Device(object):
    '''
    Scopefoundry compatible class to run a FLIR camera with spinnaker software
    For Pointgrey grasshopper, the bit depth is 16bit or 8bit, specified in the PixelFormat attribute, 
    simple_pyspin is not compatible with 12bit readout. 
    '''
    
    def __init__(self, serial = '0135500826', axis = '1'):
        self.serial = serial
        self.axis = axis
        self.pi_device = GCSDevice()                       
        self.pi_device.ConnectUSB (serial) 
        self.pi_device.RON(self.axis, True) # TODO check: set reference to OFF. 
        self.set_servo(mode = True)
        self.set_home()
        self.positive_direction = True # to be used for backslash correction
        
    def get_info(self):
        info  = f'{self.pi_device.qIDN()}'
        return info
    
    def get_servo(self):
        servomode = self.pi_device.qSVO(self.axis)[self.axis]
        return servomode
   
    def set_servo(self, mode = False): 
        self.pi_device.SVO(self.axis, mode)
        print(f'Servo set to {mode}')

    def move_absolute(self, desired_pos):
        rangemin = self.pi_device.qTMN()[self.axis]
        rangemax = self.pi_device.qTMX()[self.axis]
        pos = min(rangemax, max(desired_pos, rangemin)) 
        self.pi_device.MOV(self.axis, pos)
        
    def move_relative(self, delta):
        self.pi_device.MVR(self.axis, delta)    
        
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
            time.sleep(0.1)
            self.wait_on_target()
        else:
            print('On target')
        
    
    def correct_backslash(self):
        delta = 0.05
        pos_direction = self.positive_direction
        
        if pos_direction: 
            self.move_relative(delta) # TODO write in a proper way
            self.move_relative(-delta)
        else:
            self.move_relative(-delta)
            self.move_relative(delta)
    
    def get_velocity(self):
        vel = self.pi_device.qVEL(self.axis)[self.axis]
        return vel
        
    def set_velocity(self, desired_velocity):
        vmin = 0.01
        vmax = 10 
        if self.serial == '0135500826': # M-405 linear stage
            vmax = 0.7
        velocity = min(vmax, max(desired_velocity, vmin)) 
        self.pi_device.VEL(self.axis, velocity)
        
    def close(self):
        #self.stop()
        self.pi_device.close()
        
        
if __name__ == "__main__":
    
    motor = PI_CG_Device()
    try: 
        motor.move_relative(0.1)
        # motor.set_home()
        print('Home:', motor.get_home())
        # motor.set_velocity(0.7)
        
        print('Position:', motor.get_position())
        # motor.move_absolute(-0.1)
        # motor.wait_on_target()
        #motor.gotoRefSwitch()
        
        #print(motor.pi_device.qIDN())
        
        # print('Position:', motor.get_position())
    
    finally:
        motor.close()
    
        
    
        

        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        