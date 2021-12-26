# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 10:43:47 2020

@author: emil
"""

import nidaqmx
import numpy as np

class DAQcard:
    def __init__(self, channels=None, rate=None, samples=None, devname=None,
                 max_val=10, min_val=-10,
                 max_out=10, min_out=-10,
                 outputs=None, timeout=None, sync=None, ext_sync=None):
        self.system = nidaqmx.system.system.System()
        if devname is None:
            self.name = self.system.devices[0].name
        else:
            self.name = devname
        if (channels is not None) and (len(channels) > 0):
            self.channels = channels
            self.rate = rate
            self.samples = samples
            if timeout is None:
                self.timeout = 1.1*self.samples/self.rate
            else:
                self.timeout = timeout
            self.task = nidaqmx.Task(new_task_name='ReadTask')
            for ch in self.channels:
                self.task.ai_channels.add_ai_voltage_chan("{}/{}".format(self.name, ch), 
                                                          min_val=min_val, max_val=max_val,
                                                          terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
            # measure in the default finite samples mode
            self.task.timing.cfg_samp_clk_timing(rate=rate, samps_per_chan=samples,
                                                 sample_mode=nidaqmx.constants.AcquisitionType.FINITE)
            if sync is not None:
                print('Synchronizing DAQ to 10 MHz external clock')
                self.system.disconnect_terms("/{}/10MHzRefClock".format(self.name), 
                                             "/{}/{}".format(self.name,
                                                             sync))
                self.task.timing.ref_clk_src = "/{}/{}".format(self.name, sync)
                self.task.timing.ref_clk_rate = 10000000
        else:
            self.task = None
                
        if ext_sync is not None:
            source = "/{}/10MHzRefClock".format(self.name)
            if isinstance(ext_sync, str):
                dest = "/{}/{}".format(self.name, ext_sync)
                self.system.connect_terms(source, dest)
            else: #assuming that ext_sync is an iterable
                for port in ext_sync:
                    dest = "/{}/{}".format(self.name, port)
                    self.system.connect_terms(source, dest)
        
        if outputs is not None:
            self.write_task = nidaqmx.Task(new_task_name='WriteTask')
            if isinstance(outputs[0], tuple):
                to_write = []
                for ao, data in outputs:
                    print("Setting up DAQ ", ao)
                    self.write_task.ao_channels.add_ao_voltage_chan("{}/{}".format(self.name, ao),
                                                                    min_val=min_out, max_val=max_out)
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
                
                if sync is not None:
                    print('Synchronizing DAQ write to 10 MHz external clock')
                    self.write_task.timing.ref_clk_src = "/{}/{}".format(self.name, sync)
                    self.write_task.timing.ref_clk_rate = 10000000
            else:
                for ao in outputs:
                    print("Setting up DAQ ", ao)
                    self.write_task.ao_channels.add_ao_voltage_chan("{}/{}".format(self.name, ao),
                                                                    min_val=min_out, max_val=max_out)
        else:
            self.write_task = None
    
    def start(self):
        self.task.start()
    def stop(self):
        self.task.stop()
    def close(self):
        if self.task is not None:
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
    
    def write_scalar(self, value):
        self.write_task.write(value, auto_start=True)
        self.write_task.stop()

if __name__ == '__main__':  
    try:        
        daq = DAQcard(devname='Dev4', channels=['ai1'], rate=100, samples=100, sync='PFI0')
        data = daq.measure()
    finally:
        daq.close()
