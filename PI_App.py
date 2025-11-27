"""
****************************************
Created on Tue Jun 21 12:45:26 2021
@authors: Victoire Destombes, Andrea Bassi, Emma Martinelli. Politecnico di Milano

"""

from ScopeFoundry import BaseMicroscopeApp

class pi_app(BaseMicroscopeApp):
    name = 'pi_app'
    
    def setup(self):
        
        #Add hardware components
        print("Adding Hardware Components")
        from PI_hardware import PI_HW
        # change the serial number with your device one and the encoder you want to use
        #translator stage
        self.add_hardware(PI_HW(self, serial='0185500006', encoder='VC'))
        #voice coil
        # self.add_hardware(PI_HW(self, serial='0119024343', encoder='VC'))

if __name__ == '__main__':
    import sys
    
    app = pi_app(sys.argv)
    sys.exit(app.exec_())
