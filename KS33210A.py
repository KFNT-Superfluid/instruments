# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:56:38 2020

@author: emil
"""

class KS33210A:
    """Keysight KS33210A DC to 10 MHz signal generator."""
    
    def __init__(self, rm, address, Z='inf'):
        self.dev = rm.open_resource(address)
        self.dev.clear()
        print(self.dev.query('*IDN?'))
        self.dev.write("FUNC SIN") # set the function to sine
        self.dev.write("VOLT:UNIT VPP")
        if Z == 'inf':
            self.dev.write("OUTP:LOAD INF")
        else:
            self.dev.write("OUTP:LOAD 50")
        self.output_state = False
    
    def function(self, function):
        self.dev.write("FUNC {}".format(function.upper()))
    
    def close(self):
        self.dev.clear()
        self.dev.close()

    def amplitude(self, value=None):
        if value is not None:
            if value < 0.01:
                self.output(False)
            else:
                self.dev.write("VOLT {:.4f}".format(value))
        else:
            return self.dev.query("VOLT?")
    
    def lolevel(self, value):
        self.dev.write("VOLT:LOW {:.4f}".format(value))
    def hilevel(self, value):
        self.dev.write("VOLT:HIGH {:.4f}".format(value))
    
    def frequency(self, freq=None):
        if freq is not None:
            self.dev.write("FREQ {:.9f}".format(freq))
        else:
            return self.dev.query("FREQ?")
    
    def output(self, state=False):
        toggled = self.output_state ^ state
        self.dev.write("OUTP {}".format('ON' if state else 'OFF'))
        self.output_state = state
        return toggled

if __name__ == '__main__':
    import visa
    rm = visa.ResourceManager()
    dev = KS33210A(rm, "33210A")
    print(dev.amplitude())
    print(dev.frequency())