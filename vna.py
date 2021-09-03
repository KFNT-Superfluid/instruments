# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 12:58:45 2020

@author: ev
"""

import numpy as np
import time
from .Instrument import Instrument

class VNA(Instrument):
    """Some basic VNA functions. Most of the code stolen from Vaisakh's/Robyn's code."""

    def __init__(self, rm, address="USB0::0x2A8D::0x5D01::MY54301840::INSTR"):
        super().__init__(rm, address)
        print(self.idn())
        self.vna.timeout=20*60*1000
    
    def close(self):
        self.output_off()
        super().close()
        
    def setup(self, S='S11'):
        # set number of traces
        self.vna.write(":CALC1:PAR:COUN 3")

        # window display setting
        self.vna.write(":DISP:WIND1:SPL D13_23")

        # set S parameter for each trace
        self.vna.write(":CALC1:PAR1:DEF {}".format(S))
        self.vna.write(":CALC1:PAR2:DEF {}".format(S))
        self.vna.write(":CALC1:PAR3:DEF {}".format(S))

        # Choose data format
        self.vna.write(":CALC1:PAR1:SEL")
        self.vna.write(":CALC1:FORM MLOG")

        self.vna.write(":CALC1:PAR2:SEL")
        self.vna.write(":CALC1:FORM PHAS")

        self.vna.write(":CALC1:PAR3:SEL")
        self.vna.write(":CALC1:FORM POL")

        # turn averaging off
        self.vna.write(":SENS1:AVER OFF")
    
    def power(self, set_power=None):
        """Set or query the output power in dBm"""
        if set_power is None:
            print('Asking for power')
            return float(self.vna.query(':SOUR1:POW:LEV?'))
        self.vna.write(':SOUR1:POW:LEV {:.3f}'.format(set_power))
    
    def output_off(self):
        self.vna.write(':INIT1:CONT OFF')

    def sweep(self, start, stop, num_points=10001, bw=10e3, avg=None):
        self.vna.write(":SENS1:FREQ:STAR " +str(start))
        self.vna.write(":SENS1:FREQ:STOP " +str(stop))
        self.vna.write(":SENS1:SWE:POIN " +str(num_points))
        self.vna.write(":SENS1:BWID " +str(bw))
        
        if avg is None:
            # print("Not using averaging.")
            self.vna.write(":SENS1:AVER OFF")
        else:
            print("Averging {} times.".format(avg))
            self.vna.write(":SENS1:AVER ON")
            self.vna.write(":SENS1:AVER:COUN {}".format(avg))
            self.vna.write(":SENS1:AVER:CLE")
        
        #set trigger to cts
        self.vna.write(":INIT1:CONT ON")
        self.vna.write(":TRIG:SOUR BUS")
        self.vna.write(":TRIG:SING")

        time.sleep(1)
        self.vna.query("*OPC?")

        #Autoscale
        self.vna.write(":DISP:WIND1:TRAC1:Y:AUTO")
        self.vna.write(":DISP:WIND1:TRAC2:Y:AUTO")
        self.vna.write(":DISP:WIND1:TRAC3:Y:AUTO")

        self.vna.write(":FORM:DATA ASC")

        data3 = self.vna.query(":CALC1:TRAC3:DATA:FDATa?")
        polar = data3.split(",")
        polar = np.array(polar,dtype=float)
        polar = np.reshape(polar, [num_points,2])

        x = polar[:,0]
        y = polar[:,1]

        #frequency data
        self.vna.write(":SENS1:FREQ:DATA?")
        frequency = self.vna.read()
        freq = frequency.split(",")
        freq = np.array(freq,dtype=float)
        data = np.column_stack((freq,x,y))
        return data
    
    def sweep_cs(self, center, span, num_points=10001, bw=10e3, avg=None):
        return self.sweep(center-span/2, center+span/2, num_points, bw, avg)