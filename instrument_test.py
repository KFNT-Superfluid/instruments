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

rm = visa.ResourceManager()
 

try:
    lockin = SR830(rm, 'GPIB0::1::INSTR')
    settings = lockin.get_settings()
    print( *[str(x) + ':\t' + str(settings[x]) +'\n' for x in settings])    

finally:
    lockin.close()
    rm.close()
        
        



