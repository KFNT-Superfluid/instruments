# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 11:02:29 2020

Class to control the BNC model 865 RF source.

@author: Emil
"""

class BNC865:
    """Very basic interface to the BNC Model 865 RF source."""
    
    def __init__(self, rm, address='USB0::0x03EB::0xAFFF::4C1-3A3200905-1225::0::INSTR'):
        self.rm = rm
        self.address = address
        self.dev = self.rm.open_resource(address)
        idn = self.dev.query('*IDN?')
        print(idn)
    
    def close(self):
        """Close the VISA session."""
        self.dev.close()
    
    def frequency(self, set_freq=None):
        """Set or query the frequency in Hz."""
        if set_freq is None:
            return float(self.dev.query(':FREQ?'))
        self.dev.write(':FREQ {:.0f}'.format(set_freq))
    
    def output(self, set_status=None):
        """Set or query the output status."""
        if set_status is None:
            stat = int(self.dev.query(':OUTP?'))
            return bool(stat)
        if set_status:
            self.dev.write(':OUTP ON')
        else:
            self.dev.write(':OUTP OFF')
    
    def power(self, set_power=None):
        """Set or query the output power in dBm"""
        if set_power is None:
            return float(self.dev.query(':POW:LEV?'))
        self.dev.write(':POW:LEV {:.3f}'.format(set_power))
        
    def am(self, state=None, sens=0):
        if state is None:
            print(self.dev.query(':AM:STAT?'))
            print(self.dev.query(':AM:SOUR?'))
            print(self.dev.query(":AM:SENS?"))
            return
        if state:
            self.dev.write(':AM:SOUR EXT')
            self.dev.write(':AM:SENS {:.2f}'.format(sens))
            self.dev.write(':AM:STAT 1')
        else:
            self.dev.write(':AM:STAT 0')
        

if __name__ == '__main__':
    import visa
    rm = visa.ResourceManager()
    rf = BNC865(rm, 'USB0::0x03EB::0xAFFF::4C1-3A3200905-1225::0::INSTR')
    # rf.frequency(2.78e9)
    # rf.power(16)
    # rf.output(True)
    print(rf.frequency())
    print(rf.output())
    print(rf.power())
    rf.close()