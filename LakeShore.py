# -*- coding: utf-8 -*-
"""
Created on Sun Oct 10 16:48:11 2021

@author: ev
"""

from .Instrument import Instrument

class LakeShore(Instrument):
    def __init__(self, rm, address):
        super().__init__(rm, address)
    
    def setpoint(self, T):
        command = "SETP {:.4f}".format(T)
        self.lock()
        self.dev.write(command)
        self.clear()
        self.unlock()
        
    def read(self, channel, unit='K'):
        command = "RDG{}? {}".format(unit, channel)
        resp = self.squery(command)
        return float(resp)
    
    def control_cfg(self, channel, filt=False, units='K', delay=25,
                    cpdisp="power", htr_limit="1mA", htr_res=1000):
        
        unit_strs = {"K": 1,  "OHM": 2}
        filt_str = 1 if filt else 0
        cpdisp_strs = {"CURRENT": 1, "POWER": 2}
        htrl_confs = ['OFF', '31.6UA', '100UA', '316UA', '1MA',
                      '3.16MA', '10MA', '31.6MA', '100MA']
        htrl_strs = {k:s for k, s in enumerate(htrl_confs)}
        
        command = 'CSET {},{},{},{}, {}, {},{}'.format(channel, filt_str,
                                                       unit_strs[units.upper()], delay,
                                                       cpdisp_strs[cpdisp.upper()],
                                                       htrl_strs[htr_limit.upper()],
                                                       htr_res)
        self.lock()
        self.dev.write(command)
        self.clear()
        self.unlock()
    
    def squery(self, query):
        self.lock()
        resp = self.dev.query(query)
        self.clear()
        self.unlock()
        return resp