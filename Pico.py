#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  1 22:26:02 2024

@author: emil
"""

from .Instrument import Instrument

class Pico(Instrument):
    def __init__(self, rm, addr, access_mode='exclusive'):
        super().__init__(rm, addr, access_mode)
        
        self.configure({'read_termination': '\n',
                        'write_termination': '\n'})
    
    def LED(self, n, status):
        msg = f':LED {n} 1' if status else f':LED {n} 0'
        return self.dev.query(msg)