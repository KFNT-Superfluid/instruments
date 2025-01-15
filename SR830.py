# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 13:09:58 2020

@author: emil
"""

from .Instrument import Instrument

import time
import sys
import numpy as np
from ilock import ILock


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

sample_rates = {'62.5mHz':0,'125mHz':1,'250mHz':2,'500mHz':3,'1Hz':4,'2Hz':5,'4Hz':6,
                '8Hz':7,'16Hz':8,'32Hz':9,'64Hz':10,'128Hz':11,'256Hz':12,'512Hz':13,
                'Trigger':14}

x_display = ['X','R','X noise','AUX in 1','AUX in 2']
y_display = ['Y','Theta','Y noise','AUX in 3','AUX in 4']

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
    
    def __init__(self, rm, address, **kwargs):
        super().__init__(rm, address, **kwargs)
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
    
    def set_aux(self,n,U):
        """Sets the voltage (V) on auxiliary output n"""
        if abs(U) > 10.5:
            raise RuntimeError('Set voltage exceeds lockin limit 10.5 V')
        else:
            self.dev.write('AUXV {}, {}'.format(n,U))
    
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

    def set_display_x(self,  display:str):
        """
        Set display value on X channel.
        ----------
        display : select quantity (int)
            X   \n
            R    \n
            X noise  \n
            AUX in 1  \n
            AUX in 2   \n
        -----------
        
        Important function, because data buffer saves display values       
        """

        try:
            i = x_display.index(display)
        except:
            raise KeyError("Invalid value of 'display'")
            
        self.dev.write("DDEF {:d}, {:d}, 0".format(1, i))

        
    def set_display_y(self,  display:str):
        """
        Set display value on Y channel.
        ----------
        display : select quantity (int)
            Y   \n
            Theta    \n
            Y noise  \n
            AUX in 3  \n
            AUX in 4   \n
        -----------
        
        Important function, because data buffer saves display values       
        """
        try:
            i = y_display.index(display)
        except:
            raise KeyError("Invalid value of 'display'")
            
        self.dev.write("DDEF {:d}, {:d}, 0".format(2, i))

            
            

    def get_display_x(self):
        """
        Get display value on X channel.
        ----------
        Returns
        ----------
        display :  (int)
            0 : X  \n
            1 : R    \n
            2 : X noise  \n
            3 : AUX in 1  \n
            4 : AUX in 2   \n
        -----------
        Important function, because data buffer saves display values       
        """

        display = self.dev.query("DDEF? {:d}".format(1))
        return x_display[int(display[0])]
    
    def get_display_y(self):
        """
        Get display value on X channel.
        ----------
        Returns
        ----------
        display :  (int)
            0 : Y   \n
            1 : Theta    \n
            2 : Y noise  \n
            3 : AUX in 3  \n
            4 : AUX in 4   \n
        -----------
        Important function, because data buffer saves display values       
        """

        display = self.dev.query("DDEF? {:d}".format(2))
        return y_display[int(display[0])]
    
    def buffer_shot(self,sample_rate:str,N:int,debug:bool=False):
        """
        Measure buffer in shot mode, with given sample rate. SR830 saves data from
        CH1 and CH2 DISPLAY and stores them into the internal buffer. \n
        CH1 and CH2 display points are measured at the same time. 
        IMPORTANT: MAKE SURE LOCKIN DISPLAY IS SET TO CORRECT QUANTITY. \n
        While buffer data are transfered to PC, data transfer from other
        lockins is locked.
        
        Parameters
        ----------
        sample_rate : str
            permitted values \n
            62.5mHz  \n
            125mHz  \n
            250mHz  \n
            500mHz  \n
            1Hz  \n
            2Hz  \n
            4Hz  \n
            8Hz  \n
            16Hz  \n
            32Hz  \n
            64Hz  \n
            128Hz  \n
            256Hz  \n
            512Hz  \n
            Trigger
            
        N  : int
            number of measured points, max 16383

        debug : bool
            print progress
        Returns
        -------
        CH1 : numpy array
            measured CH1 display points
        CH2 : numpy array
            measured CH2 display points
        """ 
        try:
            i = sample_rates[sample_rate]
        except:
            raise KeyError('Invalid sample rate')
            
        self.dev.write(f'SRAT {i}')
        if N > 16383:
            raise Exception('Maximum number of measured points (16383) exceeded!')
        
       
        with ILock('aaa'):
            self.dev.write('PAUS')
            self.dev.write('REST')
            self.dev.write('STRT')
        j = 0
        
        sample_rate_float = 0.0625*2**i
        time.sleep(N/sample_rate_float +2)
        
        with ILock('aaa'):
            j = int(self.dev.query('SPTS?'))
            if j<N:
                while j+1<=N:
                    time.sleep(2)
                    j = int(self.dev.query('SPTS?'))
            self.dev.write('PAUS')
        
        if debug:
            print(f'\nNumber of points in buffer: {j}')
        
        try:
            start = time.time()
            old_timeout = self.dev.timeout
            self.dev.timeout = None
            with ILock('aaa',timeout=5*60):
                X_buffer = self.dev.query_binary_values(f'TRCB? 1,0,{N}',datatype='f',data_points = N,header_fmt='empty')
                Y_buffer = self.dev.query_binary_values(f'TRCB? 2,0,{N}',datatype='f',data_points = N,header_fmt='empty')
            self.dev.timeout = old_timeout
            end = time.time()
            if debug:
                print(f'Transfer took: {end-start}s')
        except Exception as e:
            self.dev.write('REST')
            raise Exception(f'Could not extract buffer data\nError: {e}')
        
        CH1 = np.array(X_buffer)
        CH2 = np.array(Y_buffer)
        self.dev.write('REST')
    
        return CH1,CH2
        
            
            
