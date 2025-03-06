from ScopeFoundry import HardwareComponent
from PI_ScopeFoundry.PI_CG_device import PI_CG_Device

# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 12:45:26 2021
@authors: Victoire Destombes, Andrea Bassi. Politecnico di Milano
"""

# SERIAL = '0135500826' # serial number of the M-405 linear stage

class PI_CG_HW(HardwareComponent):
    name = 'PI_CG_HW'

    def __init__(self, *args, **kwargs ):
        if 'serial' in kwargs:
            _serial = kwargs['serial']
            kwargs.pop('serial')
            self._serial = _serial
            super().__init__(*args, **kwargs)

        else:
            super().__init__(*args, **kwargs)
            self._serial = '000000000000'
    
    def setup(self):
        # create Settings (aka logged quantities)
        self.serial = self.settings.New(name='serial',dtype=str, initial = self._serial, ro=False)

        self.info = self.settings.New(name='info', dtype=str)
        # self.name = self.settings.New(name='name stages', dtype=str)
        self.target_position = self.settings.New(name='target position', dtype=float, unit='mm')
        self.position = self.settings.New(name='position', ro = True, dtype=float, unit='mm', reread_from_hardware_after_write = True)
        
        self.velocity = self.settings.New(name='velocity', dtype=float, unit='mm/s', initial = 0.5, reread_from_hardware_after_write = True)
        self.servo = self.settings.New(name='servo', initial=False, dtype=bool)
        self.home = self.settings.New(name='home', dtype=float, unit='mm')
        
        self.add_operation('SetHome', self.set_home)
        self.add_operation('GoHome', self.go_home)
        self.step = self.settings.New(name='step', dtype=float, initial = 5, unit='um')
        self.add_operation('Move', self.move_relative)
        self.add_operation('Stop', self.stop)
        self.add_operation('GotoRefSwitch', self.gotoRefSwitch)
        
        
    def connect(self):
        # connect settings to Device methods
        self.motor = PI_CG_Device(serial = SERIAL, axis = '1')     
        
        self.info.hardware_read_func = self.motor.get_info
        
        self.position.hardware_read_func = self.motor.get_position
        self.target_position.hardware_set_func = self.motor.move_absolute
        
        self.velocity.hardware_read_func = self.motor.get_velocity
        self.velocity.hardware_set_func = self.motor.set_velocity
        
        self.servo.hardware_set_func = self.motor.set_servo        
        self.servo.hardware_read_func = self.motor.get_servo        
        
        # self.home.hardware_read_func = self.motor.get_home
        
        self.read_from_hardware()
        
    def disconnect(self):
        if hasattr(self, 'motor'):
            self.motor.close() 
            del self.motor
            
        for setting in self.settings.as_list():
            setting.hardware_read_func = None
            setting.hardware_set_func = None
            
    def set_home(self):
        self.motor.set_home()
    
    def stop(self):
        self.motor.stop()
        
    def go_home(self):
        self.motor.go_home()

    def move_relative(self):
        self.motor.move_relative(self.step.value)
        self.position.read_from_hardware()
        
    def gotoRefSwitch(self):
        self.motor.gotoRefSwitch()
        
        
        
        