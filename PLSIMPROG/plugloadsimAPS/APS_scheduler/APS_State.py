'''
this module contains APS_State classes, this class controls the APS wrt. to time
'''

from APS_scheduler.Advanced_Power_Strip import AdvancedPowerStripT2 as APS_T2
from PlugLoad_Sim.inputstr_generator import InputGenerator

from collections import deque

import sys

# handling the case where a state is carried over is done by inputting negative start times

INF = float('inf')

class APSStateError(Exception):
    pass

class APS2_State:
    '''
    models trickle star APS Plus which follows this logic
    
    This power strip automatically disconnects certain devices when
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
    
    
    # Interface:
    # constructor: takes in APS class instance of the times that APS use, str_generators for generating strings
    # flush      : reset internal deque, then write to the generators, used at the end  of an input interval
    # get_state  : gets the current state should be used to determine the prompt
    # 
    
    
    # Notes on Implementation
    # all math must be done in terms of number of periods
    # use deque to add on state:time pairs to write to str_generators
    
    # modes that APS State can be in
    IR          = 'IR_only'
    IR_AND_MOVE = 'IR_and_movement'
    POWER_SAVE  = 'power_save'
    
    NEXT_STATES_SIGNAL   = {IR: IR, IR_AND_MOVE: IR, POWER_SAVE:POWER_SAVE}
    NEXT_STATES_NOSIGNAL = {IR: IR_AND_MOVE, IR_AND_MOVE: POWER_SAVE, POWER_SAVE:POWER_SAVE}
    
    def __init__(self, aps: APS_T2, time_IR, time_IR_move, interval_periods: int, start_state=IR, start_periods=0):
        # handling the case where a state is carried over is done by inputting negative start times
        # this allows the state to preserve mathematical integrity when doing the time calculations
        
        self._aps          = aps
        self._time_map     = {APS2_State.IR: time_IR, 
                              APS2_State.IR_AND_MOVE: time_IR_move, 
                              APS2_State.POWER_SAVE: INF}
        
        self._current_time = start_periods
        self._max_periods  = interval_periods
        self._time_left    = interval_periods
            
        self._state        = start_state
        self._states_times = deque()
        self._states_times.append((start_state, start_periods))
        
        self._carry_over   = 0
        
    def time_left(self):
        return self._time_left
        
    def _check_deque(self):
        return self._states_times
    
    def reset(self):
        pass
    
    def flush(self):
        '''
        call at the end of the interval flushes the deque which contains the information about the states
        and the times spent at each state
        '''
        
        
        # perform checks for the deques time adding up to the interval time
        sum = 0
        for state, time in self._states_times:
            sum += time
        if sum != self._max_periods:
            raise APSStateError('Error in aligning deque: Time alloted is greater than time in interval')
        ### add a condition to specify the return of the next needed state
        ### which is when the State is NOT in power save mode because those states can carry over with negative
        ### start times
        
        # because negative periods do not make sense the flush method will automatically popleft
        # all  state:time pairs with negative times  this does not change the write onto the string
        # because the previous instance already accounts for this
        
        # the above modification will cause some times in the deque to be negative so popleft the ones with
        # negative times
        
        if self._carry_over:
            return (self._states_times, (self._state, self._carry_over))
        
        return (self._states_times, None)
    
        # replace None with the eventual information for the start of the next state

    def check_state(self):
        return self._state
    
    def input_signal(self, time: int):
        '''
        input a signal with time after the last signal in intervals,
        this time cannot be more than the threshold until the APS changes to its next state
        if this method is called the current state is written with the amount of time until the signal
        '''
        if self._state == APS2_State.POWER_SAVE:
            raise APSStateError('State cannot be {} in method: input signal'.format(APS2_State.POWER_SAVE))
        if time > self._time_map[self._state]:
            raise APSStateError('Method: input_signal: \
            Time inputed {} is greater than maximum allowed time {} in current state: {}'.format(
            time, self._time_map[self._state], self._state))
            
        
        old_state = self._state
        self._state = APS2_State.NEXT_STATES_SIGNAL[old_state]
        
        if self._current_time < 0:
            self._states_times.append((old_state, -1))
        else:
            self._states_times.append((old_state, min(time, abs(self._time_left))))
        
        self._current_time += time
        self._time_left     = self._max_periods - self._current_time 
        
        if time > self._time_left:
            self._carry_over = abs(self._time_left)
        
    def next_state(self):
        '''
        call if there is no signal inputed within the threshold that the state provides, moves the device
        to the next state while also doing all the time consideration
        '''
        old_state   = self._state
        self._state = APS2_State.NEXT_STATES_NOSIGNAL[old_state]
        
        self._states_times.append((old_state, min(self._time_map[old_state], self._time_left)))
        
        self._current_time += min(self._time_map[old_state], self._time_left)
        self._time_left     = self._max_periods - self._current_time
    
    def __str__(self):
        return 'APS_State:\n\
max_periods={max_periods}, state={state}, t_left={t_left}, t_max={t_max},\
 current_time={current_time}'.format(max_periods=self._max_periods, state=self._state, t_left=self._time_left,
                                                t_max=self._time_left, current_time = self._current_time)  

if __name__ == '__main__':
    def print_debug_info(apsState):
        print(apsState)
        print(apsState._check_deque())
        
    test_aps = APS_T2('TV', ['dvd', 'xbox', 'sound system'], 60, move_time=75, is_on=False)
    apsState = APS2_State(test_aps, 600,750, 6000)
    
    print(apsState.check_state())
    apsState.input_signal(300)
    
    print_debug_info(apsState)
    
    apsState.next_state()
    print_debug_info(apsState)

    apsState.input_signal(300)
    print_debug_info(apsState)
    
    apsState.next_state() # IR->IR+Move
    print_debug_info(apsState)
    
    apsState.next_state() # IR+Move->Power_Save
    print_debug_info(apsState)
    
    apsState.next_state() # PowerSave->PowerSave
    print_debug_info(apsState)
        # note that to ensure powerSave is written onto the deque call another nextState()
    print(apsState.flush())
    
    print()
    
    apsState2 = APS2_State(test_aps, 600,750, 1000)
    
    apsState2.input_signal(500)
    print_debug_info(apsState2)
    
    apsState2.input_signal(400)
    print_debug_info(apsState2)
    
    apsState2.input_signal(400)
    print_debug_info(apsState2)
    
    print(apsState2.flush())
    
