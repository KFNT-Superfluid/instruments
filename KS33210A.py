# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:56:38 2020

@author: emil
"""

import numpy as np

class KS33210A:
    """Keysight KS33210A DC to 10 MHz signal generator."""
    
    def __init__(self, rm, address, Z='inf', initialize_state=True):
        self.dev = rm.open_resource(address)
        self.dev.clear()
        print(self.dev.query('*IDN?'))
        if initialize_state:
            self.dev.write("FUNC SIN") # set the function to sine
            self.dev.write("VOLT:UNIT VPP")
            if Z == 'inf':
                self.dev.write("OUTP:LOAD INF")
            else:
                self.dev.write("OUTP:LOAD 50")
        self.output_amplitude = np.nan
        self.output_amplitude = float(self.amplitude())
        self.output_state = self.output()
        
    def function(self, function):
        self.dev.write("FUNC {}".format(function.upper()))
    
    def close(self):
        self.dev.clear()
        self.dev.close()

    def amplitude(self, value=None):
        if value is not None:
            self.output_amplitude = value
            if value < 0.02:
                self.output_amplitude = 0
                self.output(False)
            else:
                self.dev.write("VOLT {:.4f}".format(value))
        else:
            if self.output_amplitude < 0.02:
                return 0
            return float(self.dev.query("VOLT?"))
    
    def lolevel(self, value):
        self.dev.write("VOLT:LOW {:.4f}".format(value))
    def hilevel(self, value):
        self.dev.write("VOLT:HIGH {:.4f}".format(value))
    
    def frequency(self, freq=None):
        if freq is not None:
            self.dev.write("FREQ {:.9f}".format(freq))
        else:
            return self.dev.query("FREQ?")
    
    def frequency_sweep(self, enable, fi=None, ff=None, t=None):
        if enable:
            self.dev.write("FREQ:STAR {:.3f}".format(fi))
            self.dev.write("FREQ:STOP {:.3f}".format(ff))
            self.dev.write("SWE:SPAC LIN")
            self.dev.write("SWE:TIME {:.3f}".format(t))
            self.dev.write("TRIG:SOUR EXT")
            self.dev.write("TRIG:SLOP POS")
            self.dev.write("SWE:STAT ON")
        else:
            self.dev.write("TRIG:SOUR IMM")
            self.dev.write("SWE:STAT OFF")
        
    def amplitude_modulation(self, enable, depth=1):
        if enable:
            self.dev.write("AM:STAT ON")
            self.dev.write("AM:SOUR EXT")
            self.dev.write("AM:DEPTH {:.4f}".format(depth))
        else:
            self.dev.write("AM:STAT OFF")
        
    def output(self, state=None):
        if state is None:
            resp = self.dev.query('OUTP?')
            return bool(resp)
        if self.output_amplitude >= 0.02:
            toggled = self.output_state ^ state
            self.dev.write("OUTP {}".format('ON' if state else 'OFF'))
            self.output_state = state
            return toggled
        else:
            self.dev.write("OUTP OFF")
            return False

if __name__ == '__main__':
    import visa
    rm = visa.ResourceManager()
    dev = KS33210A(rm, "33210A")
    print(dev.amplitude())
    print(dev.frequency())