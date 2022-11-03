# -*- coding: utf-8 -*-
"""
Created on Thu Oct  6 12:29:54 2022

@author: Filip Novotny
"""

from .Instrument import Instrument

class MKS670B(Instrument):
    def __init__ (self, rm, address):
        super().__init__(rm, address)
        self.dev.read_termination='\r'
        self.dev.write_termination='\r'
        
    def readP (self):
        resp = self.dev.query('@020?')
        self.Pressure = float(resp.split(' ')[1])
        
        return self.Pressure