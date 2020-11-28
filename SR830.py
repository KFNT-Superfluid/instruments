# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 13:09:58 2020

@author: emil
"""

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
        if sens > val:
            return scode
    return "1"
    

class SR830:
    """Stanford SR830 lockin."""
    
    def __init__(self, rm, address):
        self.dev = rm.open_resource(address)
        self.dev.clear()
        print(self.dev.query('*IDN?'))
        self.dev.write('HARM 1')
        self.dev.write("FPOP 1,1")
        self.dev.write("FPOP 2,1")
        self.dev.write('ISRC 0') # set tje input conf to A
        self.dev.write('IGND 0') # set the grounding to float
        self.set_reference('external')
        self.harmonic(1)
    
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
        self.dev.write("OFLT {}".format(time_constants[tc]))
    
    def set_sensitivity(self, sens):
        self.dev.write("SENS {}".format(sensitivities[sens]))
    
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
    
    def auto_sens(self, maxval):
        sens = find_best_sens(maxval)
        self.set_sensitivity(sens)
        return sens
    
    def close(self):
        self.dev.clear()
        self.dev.close()
    