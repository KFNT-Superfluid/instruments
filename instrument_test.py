#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 16:02:58 2023

@author: filip
"""

import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import os
import time
from time import strftime, localtime
import scipy.optimize as optim

from tqdm import tqdm

import sys
sys.path.append('C:/Software')

from instruments.SR844 import SR844
# from instruments.Rigol_DG import Rigol_DG


def res(f, A, f0, w, phi, b1, b2):
    bg = b1*(f - f0) + b2
    peak = A*f*w/(f0**2 - f**2 + 1j*f*w)*np.exp(-1j*phi)
    return np.abs(bg + peak)

def phase(f, A, f0, w, phi, b1, b2):
    peak = A*f*w/(f0**2 - f**2 + 1j*f*w)
    return np.angle(peak)


rm = visa.ResourceManager()
 

try:
    lockin = SR844(rm, 'GPIB0::8::INSTR')
    # print(lockin.harmonic(2))
    print( *[str(x) + '\t' + str(lockin.get_settings()[x]) +'\n' for x in lockin.get_settings()])    
    # print( lockin.dev.query('HARM?') )
    # print( lockin.dev.query('*IDN?') )
finally:

    lockin.close()

    rm.close()
        
        



