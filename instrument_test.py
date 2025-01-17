#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:02:58 2023

@author: filip
"""

import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np

import sys
sys.path.append('C:/Software')

from instruments.SR830 import SR830
from instruments.KS33210A import KS33210A

rm = visa.ResourceManager()
 

try:
    gen = KS33210A(rm, 'USB0::0x0957::0x1507::MY48014406::INSTR')
    settings = gen.get_settings()
    print( *[str(x) + ':\t' + str(settings[x]) +'\n' for x in settings])    
    # print(gen.output_load(50))
    # print(gen.get_FM_state())
finally:
    gen.close()
    rm.close()
        
        



