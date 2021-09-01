# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 10:43:47 2020

@author: emil
"""

import nidaqmx
import numpy as np

class DAQcard:
    def __init__(self, channels, rate, samples, devname=None, max_val=10, min_val=-10,
                 outputs=None, timeout=None):
        if devname is None:
            self.name = nidaqmx.system.system.System().devices[0].name
        else:
            self.name = devname
        self.channels = channels
        self.rate = rate
        self.samples = samples
        if timeout is None:
            self.timeout = 1.1*self.samples/self.rate
        else:
            self.timeout = timeout
        self.task = nidaqmx.Task()
        for ch in self.channels:
            self.task.ai_channels.add_ai_voltage_chan("{}/{}".format(self.name, ch), 
                                                      min_val=min_val, max_val=max_val,
                                                      terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
        # measure in the default finite samples mode
        self.task.timing.cfg_samp_clk_timing(rate=rate, samps_per_chan=samples,
                                             sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
        
        if outputs is not None:
            self.write_task = nidaqmx.Task()
            if isinstance(outputs, tuple):
                _outputs = [outputs]
            else:
                _outputs = outputs
            to_write = []
            for ao, data in _outputs:
                print("Setting up DAQ ", ao)
                self.write_task.ao_channels.add_ao_voltage_chan("{}/{}".format(self.name, ao))
                to_write.append(data)
                
            self.write_task.timing.cfg_samp_clk_timing(rate=rate, samps_per_chan=len(data),
                                                       sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
            if len(to_write) == 1:
                to_write = to_write[0]
            else:
                to_write = np.array(to_write)
            self.write_task.write(to_write, auto_start=False, timeout=self.timeout)
            #configure the write to trigger on read start trigger
            self.write_task \
                .triggers \
                .start_trigger \
                .cfg_dig_edge_start_trig(r"/{}/ai/StartTrigger".format(self.name))
        else:
            self.write_task = None
    
    def start(self):
        self.task.start()
    def stop(self):
        self.task.stop()
    def close(self):
        self.task.close()
        if self.write_task is not None:
            self.write_task.close()
    
    def write_measure(self):
        self.write_task.start()
        self.task.start()
        data = self.task.read(nidaqmx.constants.READ_ALL_AVAILABLE, timeout=self.timeout)
        self.task.stop()
        self.write_task.stop()
        return np.array(data)
    
    def measure(self):
        self.start() #this also starts the writing if configured
        data = self.task.read(nidaqmx.constants.READ_ALL_AVAILABLE, timeout=self.timeout)
        self.stop()
        return np.array(data)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # plt.close('all')

    rate = 4094
    samples = int(rate*16)
    output = np.ones(int(samples/2))
    output[-1] = 0
    # output[:int(samples/2)] = 1
    freqs = np.fft.rfftfreq(samples, 1/rate)
    
    try:
        # daq = DAQcard(channels=['ai0'], rate=rate, samples=samples,
        #               outputs=('ao0', output))

        # fig, ax = plt.subplots(1,1)
        # ax.plot(output)
        # for k in range(5):
        #     data = daq.write_measure()
        #     ax.plot(data)
        
        
        daq = DAQcard(channels=['ai0'], rate=rate, samples=samples)
        avgresp = 0
        N = 5
        for k in range(N):
            print(k)
            data1 = daq.measure()
            resp = np.fft.rfft(data1)#data1[0, :] + 1j*data1[1, :])
            avgresp += abs(resp)
            # ax.plot(freqs, np.abs(avgresp)/(k+1))
        avgresp = avgresp/N
        fig, ax = plt.subplots(1, 1)
        ax.semilogy(freqs, np.abs(avgresp))
    finally:
        daq.close()
