'''
Created on Apr 11, 2016

@author: Klint
'''

# todo
#  allow method to add devices
#  cap slave devices
class APSError(Exception):
    pass

class AdvancedPowerStripT1:
    '''
    set this up later
    '''
    pass

class AdvancedPowerStripT2:
    
    ''' This class models an advanced power strip logic 
    , power strip that automatically disconnects certain devices when
    certain conditions are met. Ie. No Infrared is Sensed and/or No Movement
    
    Diagram of the APS logic
    
    IR -> switch devices on(standby) -> user turns TV on <----------------
                                            |                            ^
                                           \/                            |
                           [time_limit] minutes of IR only detection -> YES <---
                                            |                                   |
                                           \/                                   | 
                                           NO --> [move_time] IR OR Movement-->YES
                                            |
                                           \/
                                          TV off --> slave devices off                 
    '''
    
    def __init__(self, master_devices: str, slave_devices: list, time_limit: int, move_time=0, is_on = False):
        self._master_device     = master_devices
        self._slave_devices     = slave_devices
        self._move_time         = move_time
        self._time_limit        = time_limit
        self._music_mode        = False
        
        self._master_device_on  = is_on
        self._slave_devices_on  = is_on
        
    def turn_on_master_device(self):
        self._master_device_on  = True
        self._slave_devices_on  = True
        self._music_mode = False
        
    def turn_off_master_device(self):
        self._master_device_on  = False
        
        if not self._music_mode:
            self._slave_devices_on = False
    
    def turn_on_music_mode(self):
        self._music_mode = True
        self._master_device_on = False
        self._slave_devices_on = True
        
    def turn_off_music_mode(self):
        self._music_mode = False
        self._slave_devices_on = self._master_device_on
    
    def is_music_mode(self):
        return self._music_mode
    
    def master_device_on(self):
        return self._master_device_on
    
    def slave_devices_on(self):
        return self._slave_devices_on
    
    def device_detects_movement(self):
        return self.move_time > 0
            
    def time_IR_only(self):
        return self._time_limit
    
    def time_IR_and_movement(self):
        return self._move_time
    
    def master_device(self):
        return self._master_device
    
    def slave_devices(self):
        return self._slave_devices

def APST2_simp_test():
    test_aps = AdvancedPowerStripT2('TV', ['dvd', 'xbox', 'sound system'], 60, move_time=75, is_on=False)
    
    assert(not test_aps.master_device_on())
    assert(not test_aps.slave_devices_on())
    
    test_aps.turn_on_master_device()
    assert(test_aps.master_device_on())
    assert(test_aps.slave_devices_on())
    
    test_aps.turn_on_music_mode()
    assert(not test_aps.master_device_on())
    assert(test_aps.slave_devices_on())
    
    test_aps.turn_off_music_mode()
    assert(not test_aps.slave_devices_on())
    
    test_aps.turn_on_music_mode()
    assert(not test_aps.master_device_on())
    assert(test_aps.slave_devices_on())
    
    test_aps.turn_on_master_device()
    assert(not test_aps.is_music_mode())
    assert(test_aps.slave_devices_on())
    assert(test_aps.master_device_on())

if __name__ == '__main__':
    APST2_simp_test()

    