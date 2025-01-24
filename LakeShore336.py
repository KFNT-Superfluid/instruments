#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 14:49:05 2023

@author: filip
"""

import numpy as np
import scipy.interpolate as intp
import pyvisa as visa
from pyvisa.constants import Parity
from time import sleep
from .Instrument import Instrument

class LakeShore336(Instrument):
    def __init__ (self, rm, address, **kwargs):
        super().__init__(rm, address, **kwargs)
        self.dev.baud_rate = 57600
        self.dev.data_bits = 7
        self.dev.parity = Parity.odd
        self.calibration = {}
    
    def add_calibration(self, channel, file):
        data = np.loadtxt(file)
        R = data[:,0]
        T = data[:,1]
        self.calibration[channel] = intp.interp1d(R, T, bounds_error=False, fill_value='extrapolate')
        
    def set_manual_control(self, max_power):
        self.dev.write("CMODE 1,3") # set to open loop control
        self.dev.write("CLIMIT 1,,,,5,")
        self.dev.write("CLIMI 0.1")
        self.dev.write('RANGE 4') # heater range up-to 
    
    def manual_heat(self, power=None):
        if power is None:
            return float(self.squery("MOUT?"))
        command = "MOUT {:.3E}".format(power)
        self.dev.write(command)
        
    def read(self, channel, unit='K', softcal=True):
        '''
        K = Kelvin
        C = Celsius
        S = Sensor imput (Ohm)
        
        channel = A,B,C,D, 0 = all
        '''
        do_softcal = False
        if unit=='K' and softcal and channel in self.calibration:
            do_softcal=True
            unit = 'S'
        command = '{}RDG? {}'.format(unit, channel)
        resp = float(self.dev.query(command))
        if do_softcal:
            T = self.calibration[channel](resp).item()
            # print(T)
            return T
        return resp
         
        