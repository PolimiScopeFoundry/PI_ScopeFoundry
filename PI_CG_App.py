"""
****************************************
Created on Tue Jun 21 12:45:26 2021
@authors: Victoire Destombes, Andrea Bassi, Emma Martinelli. Politecnico di Milano

"""

from ScopeFoundry import BaseMicroscopeApp

class pi_cg_app(BaseMicroscopeApp):
    

    name = 'pi_cg_app'
    
    def setup(self):
        
        #Add hardware components
        print("Adding Hardware Components")
        from PI_CG_hardware import PI_CG_HW
        self.add_hardware(PI_CG_HW(self, serial='0115500028'))



if __name__ == '__main__':
    import sys
    
    app = pi_cg_app(sys.argv)
    sys.exit(app.exec_())
