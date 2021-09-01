# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 13:09:58 2020

@author: emil
"""

import visa

tcs = ["10u", "30u", "100u", "300u",
       "1m", "3m", "10m", "30m", "100m", "300m",
       "1", "3", "10", "30", "100", "300",
       "1k", "3k", "10k", "30k"]

time_constants = {val:code for code, val in enumerate(tcs)}


senss = ["2n", "5n", "10n", "20n", "50n", "100n", "200n", "500n",
         "1u", "2u", "5u", "10u", "20u", "50u", "100u", "200u", "500u",
         "1m", "2m", "5m", "10m", "20m", "50m", "100m", "200m", "500m",
         "1"]

sensitivities = {val:code for code, val in enumerate(senss)}

fslps = ['6', '12', '18', '24']
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
    

class SR830:
    """Stanford SR830 lockin."""
    
    def __init__(self, rm, address):
        self.dev = rm.open_resource(address, access_mode=visa.constants.AccessModes.shared_lock)
        self.locked=False
    
    def clear(self):
        self.dev.clear()
    
    def lock(self, timeout=5000):
        self.dev.lock(timeout=timeout)
        self.locked=True
    def unlock(self):
        self.dev.unlock()
        self.locked=False
    
    def phase(self, phi=None):
        if phi is None:
            return float(self.dev.query('PHAS?'))
        else:
            self.dev.write('PHAS {:.3f}'.format(phi))
        
    def get_aux(self, n):
        return float(self.dev.query('OAUX? {}'.format(n)))
    
    def coupling(self, cpl):
        if cpl.upper() == 'AC':
            self.dev.write('ICPL 0')
        elif cpl.upper() == 'DC':
            self.dev.write('ICPL 1')
        else:
            raise RuntimeError("Unknown coupling {}, only DC or AC allowed".format(cpl))
    
    def set_reserve(self, res):
        reserves = {'HIGH': 0, 'NORMAL': 1, 'LOW': 2}
        try:
            self.dev.write("RMOD {}".format(reserves[res.upper()]))
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
        print("Setting tc")
        self.dev.write("OFLT {}".format(time_constants[tc]))
        print("OK")
    
    def set_sensitivity(self, sens):
        self.dev.write("SENS {}".format(sensitivities[sens]))
    
    def get_sensitivity(self):
        return code_to_value(senss[int(self.dev.query("SENS?"))])
    
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
        resp = int(self.dev.query('LIAS? 2'))
        self.dev.clear()
        return bool(resp)
    
    def close(self):
        self.dev.close()
    