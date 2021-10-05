# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:56:38 2020

@author: emil
"""

from .Instrument import Instrument
import re

class DS345(Instrument):
    """Stanford DS345 DC to 30 MHz signal generator."""
    
    def __init__(self, rm, address):
        super().__init__(rm, address)
        print(self.dev.query('*IDN?'))
        self.dev.write("FUNC 0") # set the function to sine
        self.output_amplitude = self.amplitude() 
        self.output_state = (self.output_amplitude > 0)
            
    def output(self, state):
        if state:
            self.amplitude(self.output_amplitude)
            self.output_state = True
        else:
            self.amplitude(0)
            self.output_state = False

    def amplitude(self, value=None, unit='VP'):
        if value is not None:
            if unit not in ['VP', 'VR', 'DB']:
                raise RuntimeError("Unknown amplitude unit {}".format(unit))
            self.dev.write("AMPL {:.4f} {}".format(value, unit))
            self.output_amplitude=value
            if value > 0:
                self.output_state = True
        else:
            resp = self.dev.query("AMPL?")
            units_str_match = re.search('[A-Z]+', resp)
            return float(resp[:units_str_match.start()])
    
    def set_AM_depth(self, value=0):
        self.dev.write('DPTH {:.0f}'.format(value))
    
    def frequency(self, freq=None):
        if freq is not None:
            self.dev.write("FREQ {:.3f}".format(freq))
        else:
            return self.dev.query("FREQ?")