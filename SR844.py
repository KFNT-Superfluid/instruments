# -*- coding: utf-8 -*-
"""
Created on Thu July  7 15:00 2022

@author: Emil
"""

from .Instrument import Instrument

import time

tcs = ["100u", "300u",
       "1m", "3m", "10m", "30m", "100m", "300m",
       "1", "3", "10", "30", "100", "300",
       "1k", "3k", "10k", "30k"]

time_constants = {val:code for code, val in enumerate(tcs)}


senss = ["100n", "300n", "1u", "3u", "10u", "30u", "100u", "300u",
         "1m", "3m", "10m", "30m", "100m", "300m", "1"]

sensitivities = {val:code for code, val in enumerate(senss)}
sensitivities_r = {code:val for code, val in enumerate(senss)}

fslps = ['nofilter', '6', '12', '18', '24']
lpfslopes = {val:code for code, val in enumerate(fslps)}

suffixes = {'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'k': 1e3}
def code_to_value(code):
    if code[-1] in suffixes:
        return float(code[:-1])*suffixes[code[-1]]
    else:
        return float(code)

def find_best_sens(val):
    for scode in senss:
        sens = code_to_value(scode)
        if sens > 1.5*val:
            return scode
    return "1"

channels = {'X': 1, 'Y': 2, 'R': 3}

class SR844(Instrument):
    """Stanford SR830 lockin."""
    
    def __init__(self, rm, address):
        super().__init__(rm, address)
        self.sensitivities = sensitivities
        self.sensitivities_r = sensitivities_r
        
    def phase(self, phi=None):
        if phi is None:
            return float(self.dev.query('PHAS?'))
        else:
            self.dev.write('PHAS {:.3f}'.format(phi))
    
    def auto_phase(self):
        self.dev.write('APHS')
    
    def auto_offset(self, channel='X'):
        self.dev.write('AOFF {}'.format(channels[channel]))
        
    def auto_gain(self):
        self.dev.write('AGAN')
    
    def offset_expandq(self, channel):
        expands = {0: 1, 1: 10, 2: 100}
        resp = self.dev.query('DEXP? {}'.format(channels[channel]))
        off_str, exp_str = resp.split(',')
        offset = float(off_str)
        expand = expands[int(exp_str)]
        return offset, expand
    
    def offset_expand(self, channel, expand=1, offset='auto'):
        if offset == 'auto':
            self.auto_offset(channel)
            offset, _ = self.offset_expandq(channel)
        expands = {1: 0, 10: 1, 100: 2}
        command = "OEXP {}, {}, {}".format(channels[channel], offset, expands[expand])
        self.dev.write(command)
        
    def get_aux(self, n):
        return float(self.dev.query('AUXI? {}'.format(n)))
    
    def input_impedance(self, imp):
        if imp == '50':
            self.dev.write('INPZ 0')
        elif imp.upper() == 'HIZ':
            self.dev.write('INPZ 1')
        else:
            raise RuntimeError("Unknown coupling {}, only '50' (50 Ohm) or 'HIZ' (1 Mohm) allowed".format(imp))
    
    def set_reserve(self, res):
        """Available options are 'high', 'normal' and 'low'."""
        reserves = {'HIGH': 0, 'NORMAL': 1, 'LOW': 2}
        try:
            self.dev.write("WRSV {}".format(reserves[res.upper()]))
        except KeyError:
            print("Only 'high', 'normal' and 'low' reserves are available.")
            raise
    
    def set_reference(self, ref):
        if ref=='external':
            self.dev.write('FMOD 0') # external reference
        elif ref=='internal':
            self.dev.write('FMOD 1') # internal reference
        else:
            raise RuntimeError("bad reference option: {}".format(ref))
        
    def harmonic(self, harm=None):
        if harm is None:
            return int(self.dev.query('HARM?'))
        else:
            self.dev.write('HARM {}'.format(harm))
    
    def set_timeconstant(self, tc):
        # print("Setting tc")
        self.dev.write("OFLT {}".format(time_constants[tc]))
        # print("OK")
    
    def set_sensitivity(self, sens):
        self.dev.write("SENS {}".format(sensitivities[sens]))
    
    def get_sensitivity(self, return_code=False):
        code = int(self.dev.query("SENS?"))
        if return_code:
            return code
        return code_to_value(senss[code])
    
    def set_slope(self, slope):
        self.dev.write("OFSL {}".format(lpfslopes[slope]))
        
    def set_output_amplitude(self, A):
        self.dev.write("SLVL {:.3f}".format(A))
    
    def get_output_amplitude(self):
        return float(self.dev.query("SLVL?"))

    def set_frequency(self, freq):
        """Set the demodulation frequency to freq, only for the internal reference mode."""
        self.dev.write('FREQ {:.3f}'.format(freq))
    
    def get_frequency(self):
        return float(self.dev.query('FREQ?'))
    
    def get_xy(self):
        resp = self.dev.query("SNAP? 1,2")
        xstr, ystr = resp.split(',')
        x = float(xstr)
        y = float(ystr)
        return x, y
    
    def auto_sens(self, maxval, do_set=True):
        sens = find_best_sens(maxval)
        if do_set:
            self.set_sensitivity(sens)
        return code_to_value(sens)
    
    def overloadp(self):
        status = int(self.dev.query('LIAS?'))
        self.dev.clear()
        inputo = bool(status & (1 << 0))
        filtro = bool(status & (1 << 1))
        outputo = bool(status & (1 << 2))
        return (inputo or filtro or outputo)
    