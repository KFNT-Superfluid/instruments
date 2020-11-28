# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 16:15:46 2020

@author: emil
"""

class SG384:
    """Stanford SG384 signal generator (up-to 4 GHz)"""
    
    def __init__(self, rm, address):
        self.dev = rm.open_resource(address)
        self.dev.clear()
        print(self.dev.query('*IDN?'))

    def close(self):
        self.dev.clear()
        self.dev.close()
        
    def output(self, outp=None):
        if outp is None:
            return bool(int(self.dev.query('ENBR?')))
        self.dev.write('ENBR {}'.format(1 if outp else 0))

    def frequency(self, freq=None):
        if freq is None:
            return float(self.dev.query('FREQ?'))
        self.dev.write('FREQ {:.9f}'.format(freq))
    
    def power(self, ampl=None):
        if ampl is None:
            return float(self.dev.query('AMPR?'))
        self.dev.write('AMPR {:.2f}'.format(ampl))
    
    def BNCamp(self, ampl=None):
        """Set the amplitude in peak-to-peak voltage."""
        if ampl is None:
            return float(self.dev.query('AMPL? VPP'))
        if ampl > 0.002:
            self.dev.write('AMPL {:.3f} VPP'.format(ampl))
            self.enableLF(True)
        else:
            self.enableLF(False)
    
    def enableLF(self, status=None):
        if status is None:
            return self.dev.query('ENBL?')
        self.dev.write('ENBL {}'.format(1 if status else 0))
    
    def enableRF(self, status=None):
        if status is None:
            return self.dev.query('ENBR?')
        self.dev.write('ENBR {}'.format(1 if status else 0))


if __name__ == '__main__':
    import visa
    rm = visa.ResourceManager()
    dev = SG384(rm, 'GPIB0::3::INSTR')
    print(dev.output())
    print(dev.frequency())
    print(dev.power())
    print(dev.BNCamp())
    dev.close()
