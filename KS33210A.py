# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 12:56:38 2020

@author: emil
"""

import numpy as np
import time
from .Instrument import Instrument

class KS33210A(Instrument):
    """Keysight KS33210A DC to 10 MHz signal generator.
        \nWorks for other KS332xxx series signal generators    
    """
    
    def __init__(self, rm, address, Z='inf', initialize_state=True, **kwargs):
        super().__init__(rm, address, **kwargs)
        print(self.idn())
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

    def amplitude(self, value=None, unit=None):
        """Availale units are VPP, VRMS and DBM"""
        if unit is not None:
            self.dev.write('VOLT:UNIT {}'.format(unit))
        if value is not None:
            self.output_amplitude = value
            if value < 0.01:
                self.output_amplitude = 0
                self.output(False)
            else:
                self.dev.write("VOLT {:.4f}".format(value))
        else:
            if self.output_amplitude < 0.01:
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
        
    def amplitude_modulation(self, enable, depth):
        """Specify the modulation depth in percent in the range 0 -- 120"""
        if enable:
            self.dev.write("AM:STAT ON")
            self.dev.write("AM:SOUR EXT")
            self.dev.write("AM:DEPTH {:.4f}".format(depth))
        else:
            self.dev.write("AM:STAT OFF")
        
    def amplitude_modulation_int(self, enable, depth):
        """Specify the modulation depth in percent in the range 0 -- 120"""
        if enable:
            self.dev.write("AM:STAT ON")
            self.dev.write("AM:SOUR INT")
            self.dev.write("AM:DEPTH {:.4f}".format(depth))
        else:
            self.dev.write("AM:STAT OFF")
            
    def modulation_frequency (self, freq):
        self.dev.write("AM:INT:FREQ {:.9f}".format(freq))
       
    
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
    
    def load_arb(self, waveform, name=None):
        if len(waveform)>8192:
            raise ValueError("Maximum 8192 points allowed.")
        waveform_txt = ""
        for point in waveform:
            waveform_txt += ',{:.4f}'.format(point)
            # print(point)
        old_timeout = self.dev.timeout
        # print("Starting download.")
        self.dev.timeout = 60000 #60 s
        self.dev.write(':data volatile'+waveform_txt)
        self.dev.timeout = old_timeout
        # print("Download finished.")
        # time.sleep(2)
        if name is not None:
            # print("Copying")
            self.dev.write(':data:copy '+name)
            # time.sleep(2)
    def select_arb(self, name):
        # print("Selecting arb")
        self.dev.write(':func:user '+name)
        self.dev.write(':func user')
        # time.sleep(2)
    def burst(self, enable, N=1, source = 'bus',trig_delay = 0):
        """
        Parameters
        ----------
        enable : Bool
            enable/disable burst mode
        N : Int, optional
            Number of cycles. The default is 1.
        source : Str, optional
            trigger source, options:
                bus - remote triggered \n
                ext - triggered from rear pannel bnc\n
            Default is 'bus', to trigger by bus use function 'gen.trig()'
        trig_delay : Float, optional
            set trigger delay in seconds, default is 0
            
        Returns
        -------
        None.

        """
        if enable:
            self.dev.write(':burst:mode trig')
            self.dev.write(f':trig:sour {source}')
            self.dev.write(':trig:slop pos')
            self.dev.write(f':trig:del {trig_delay}')
            self.dev.write(':burst:ncyc {:d}'.format(N))
            self.dev.write(':burst:state on')
        else:
            self.dev.write(':burst:state off')
    def trig(self):
        self.dev.write('TRIG')

    def output_load(self,Z=None):
        if Z>=1 and Z<=10_000:
            self.dev.write('OUTP:LOAD {}'.format(Z))
        elif not Z == None:
            raise RuntimeError('Invalid value of "Z" supplied: "{}"'.format(Z))
        load = int(self.dev.query('OUTP:LOAD ?'))
        return load
        

    def get_settings(self):
        
        return




        