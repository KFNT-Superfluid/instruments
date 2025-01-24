#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 09:39:52 2023

@author: filip
"""
import pyvisa as visa 
import numpy as np
from time import sleep

from .Instrument import Instrument

class Keithley(Instrument):
    
    def __init__ (self, rm, address, **kwargs):
        super().__init__(rm, address, **kwargs)
        
    def channel(self, channel):
        '''
        Parameters
        ----------
        channel : string
        
        choose outup channel: CH1, CH2, CH3

        '''
        command = f'INST:SEL {channel}'
        self.dev.write(command)
        sleep(1)
        ch = self.dev.query('INST:SEL?')
        return ch
        
    def setvoltage(self, volt):
        command = 'VOLT {:.3f}V'.format(volt)
        self.dev.write(command)
        
    def getvoltage(self):
        command = 'FETC:VOLT?'
        set_volt = self.dev.query(command)
        return float(set_volt)
    
    def setcurrent(self,curr):
        command = 'CURR {:.3f}A'.format(curr)
        self.dev.write(command)
        
    def getcurrent(self):
        command = 'FETC:CURR?'
        set_curr = self.dev.query(command)
        return float(set_curr)
    
    def output(self, oper = False):
        if oper == True:
            #command1 = 'OUTP:ENAB 1'
            command2 = 'OUTP ON'
        if oper == False:
            #command1 = 'OUTP:ENAB 0'
            command2 = 'OUTP OFF'
        #self.dev.write(command1)
        self.dev.write(command2)
        return self.dev.query('OUTP?')
        
        
        
        