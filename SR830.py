# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 13:09:58 2020

@author: emil
"""

from .Instrument import Instrument

import time

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
sensitivities_r = {code:val for code, val in enumerate(senss)}

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

channels = {'X': 1, 'Y': 2, 'R': 3}

class SR830(Instrument):
    """Stanford SR830 lockin."""
    
    def __init__(self, rm, address):
        super().__init__(rm, address)
        self.sensitivities = sensitivities
        self.sensitivities_r = sensitivities_r
        
    def phase(self, phi=None):
        """ Sets or queries the phase in degree."""
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
        resp = self.dev.query('OEXP? {}'.format(channels[channel]))
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
        """Reads the auxiliary input n."""
        return float(self.dev.query('OAUX? {}'.format(n)))
    
    def coupling(self, cpl):
        """Sets the coupling to 'AC' or 'DC'."""
        if cpl.upper() == 'AC':
            self.dev.write('ICPL 0')
        elif cpl.upper() == 'DC':
            self.dev.write('ICPL 1')
        else:
            raise RuntimeError("Unknown coupling {}, only DC or AC allowed".format(cpl))
    
    def set_reserve(self, res):
        """Available options are 'high', 'normal' and 'low'."""
        reserves = {'HIGH': 0, 'NORMAL': 1, 'LOW': 2}
        try:
            self.dev.write("RMOD {}".format(reserves[res.upper()]))
        except KeyError:
            print("Only 'high', 'normal' and 'low' reserves are available.")
            raise
    
    def set_reference(self, ref):
        """ Sets the reference to 'external' or 'internal'."""
        if ref=='external':
            self.dev.write('FMOD 0') # external reference
        elif ref=='internal':
            self.dev.write('FMOD 1') # internal reference
        else:
            raise RuntimeError("bad reference option: {}".format(ref))
        
    def harmonic(self, harm=None):
        """
        Sets or queries the harmonic

        Parameters
        ----------
        harm : int or None, optional
            Sets the harmonic to this number. If None, queries and returns the set harmonic. The default is None.

        Returns
        -------
        int
            The harmonic set on the instrument. Does not return anything if harm is a number.
        """
        if harm is None:
            return int(self.dev.query('HARM?'))
        else:
            self.dev.write('HARM {}'.format(harm))
    
    def set_timeconstant(self, tc):
        """
        Sets the time constant

        Parameters
        ----------
        tc : string
            The time constant in the format as written on the front panel of the instrument.
            "10m", "30m", "100m" would be 10ms, 30ms and 100ms, and so on ("10u" is minimum)

        Returns
        -------
        None.

        """
        # print("Setting tc")
        self.dev.write("OFLT {}".format(time_constants[tc]))
        # print("OK")
    
    def set_sensitivity(self, sens):
        """
        Sets the sensitivity.

        Parameters
        ----------
        sens : string
            The sensitivity in the format as written on the front panel of the instrument for voltage measurement.
            "10m", "20m", "50m" would be 10mV, 20mV, 50mV and so on.

        Returns
        -------
        None.

        """
        self.dev.write("SENS {}".format(sensitivities[sens]))
    
    def get_sensitivity(self, return_code=False):
        code = int(self.dev.query("SENS?"))
        if return_code:
            return code
        return code_to_value(senss[code])
    
    def set_slope(self, slope):
        """ Set the low-pass filter slope. Options are '6', '12', '18', '24'."""
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
