# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 11:31:09 2021

Base class to represent instruments. Only opening and access control.

@author: emil
"""

import pyvisa as visa

class Instrument:
    def __init__(self, rm, address):
        self.rm = rm
        self.address = address
        self.dev = rm.open_resource(address, access_mode=visa.constants.AccessModes.shared_lock)
        self.locked = False
    
    def lock(self, timeout=5000):
        self.dev.lock(timeout=timeout)
        self.locked = True
        
    def unlock(self):
        self.dev.unlock()
        self.locked = False
        
    def idn(self):
        return self.dev.query('*IDN?')
    
    def clear(self):
        self.dev.clear()
        
    def close(self):
        if self.locked:
            self.clear()
            self.unlock()
        self.dev.close()