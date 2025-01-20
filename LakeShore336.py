#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 14:49:05 2023

@author: filip
"""

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
        
        
    def read(self, channel, unit='K'):
        '''
        K = Kelvin
        C = Celsius
        S = Sensor imput (Ohm)
        
        channel = A,B,C,D, 0 = all
        '''
        command = '{}RDG? {}'.format(unit, channel)
        resp = self.dev.query(command)
        return float(resp)
         
        