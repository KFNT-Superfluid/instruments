# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 10:43:47 2020

@author: emil
"""

import nidaqmx
import numpy as np

class DAQcard:
    def __init__(self, channels, rate, samples, devname=None):
        if devname is None:
            self.name = nidaqmx.system.system.System().devices[0].name
        else:
            self.name = devname
        self.channels = channels
        self.rate = rate
        self.samples = samples
        self.task = nidaqmx.Task()
        for ch in self.channels:
            self.task.ai_channels.add_ai_voltage_chan("{}/{}".format(self.name, ch), min_val=-10, max_val=10)
        # measure in the default finite samples mode
        self.task.timing.cfg_samp_clk_timing(rate=rate, samps_per_chan=samples)
    
    def start(self):
        self.task.start()
    def stop(self):
        self.task.stop()
    def close(self):
        self.task.close()
    
    def measure(self):
        self.start()
        data = self.task.read(nidaqmx.constants.READ_ALL_AVAILABLE, timeout=512)
        self.stop()
        return np.array(data)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # from DS345 import DS345
    # from SG384 import SG384
    import visa
    
    # rm = visa.ResourceManager()
    # rf = SG384(rm, 'GPIB0::27::INSTR')
    # gen = DS345(rm, 'GPIB0::2::INSTR')
    rate = 8192
    samples = int(rate*32)
    daq = DAQcard(channels=['ai1', 'ai2'], rate=rate, samples=samples)
    fdemod = 4096
    try:
        # rf.frequency(2.72356e9)
        # rf.output(True)
        # rf.power(16)
        # gen.frequency(fdemod)
        
        # plt.close('all')
        fig, ax = plt.subplots(1,1)
        
        
        freqs = np.fft.fftfreq(samples, 1/rate)
        freqs = np.fft.fftshift(freqs) + fdemod
        
        avgresp = 0
        N = 5
        for k in range(N):
            print(k)
            data1 = daq.measure()
            resp = np.fft.fft(data1[0, :] + 1j*data1[1, :])
            resp = np.fft.fftshift(resp)
            avgresp += np.abs(resp)
            # ax.plot(freqs, np.abs(avgresp)/(k+1))
        avgresp = avgresp/N
        ax.plot(freqs, np.abs(avgresp))
    finally:
        daq.close()
        # rf.close()
        # gen.close()
        # rm.close()