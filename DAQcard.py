# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 10:43:47 2020

@author: emil
"""

import nidaqmx
import numpy as np

class DAQcard:
    def __init__(self, channels, rate, samples, devname=None, max_val=10, min_val=-10):
        if devname is None:
            self.name = nidaqmx.system.system.System().devices[0].name
        else:
            self.name = devname
        self.channels = channels
        self.rate = rate
        self.samples = samples
        self.task = nidaqmx.Task()
        for ch in self.channels:
            self.task.ai_channels.add_ai_voltage_chan("{}/{}".format(self.name, ch), 
                                                      min_val=min_val, max_val=max_val,
                                                      terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
        # measure in the default finite samples mode
        self.task.timing.cfg_samp_clk_timing(rate=rate, samps_per_chan=samples)
    
    def start(self):
        self.task.start()
    def stop(self):
        self.task.stop()
    def close(self):
        self.task.close()
    
    def measure(self, timeout=512):
        self.start()
        data = self.task.read(nidaqmx.constants.READ_ALL_AVAILABLE, timeout=timeout)
        self.stop()
        return np.array(data)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from SR830 import SR830
    from rfsource import BNC865
    import visa
    
    rm = visa.ResourceManager()
    lockin = SR830(rm, 'GPIB0::1::INSTR')
    rate = 16384
    samples = int(rate*64)
    daq = DAQcard(channels=['ai0'], rate=rate, samples=samples)
    # fdemod = 4e3
    # lockin.lock()
    # lockin.set_reference('internal')
    # lockin.set_frequency(fdemod)
    # lockin.set_timeconstant('100u')
    # lockin.unlock()
    # lockin.set_sensitivity('1m')
    # rf = BNC865(rm, 'BNC845')
    try:
        # rf.frequency(2.72356e9)
        # rf.output(True)
        # rf.power(-15)
        # gen.frequency(fdemod)
        
        # plt.close('all')
        fig, ax = plt.subplots(1,1)
        
        
        freqs = np.fft.rfftfreq(samples, 1/rate)
        freqs = np.fft.fftshift(freqs)# + fdemod
        
        avgresp = 0
        N = 10
        for k in range(N):
            print(k)
            data1 = daq.measure()
            resp = np.fft.rfft(data1)#data1[0, :] + 1j*data1[1, :])
            resp = np.fft.fftshift(resp)
            avgresp += np.abs(resp)
            # ax.plot(freqs, np.abs(avgresp)/(k+1))
        avgresp = avgresp/N
        ax.semilogy(freqs, np.abs(avgresp))
    finally:
        daq.close()
        # rf.close()
        # gen.close()
        # rm.close()