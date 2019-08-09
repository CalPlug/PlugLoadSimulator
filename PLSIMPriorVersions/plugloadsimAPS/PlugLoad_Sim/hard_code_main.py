'''
Created on Apr 15, 2016

@author: Klint

#In current demo hard coded state the LG LED HiDef TV, Microsoft Xbox One, and Dolby Surround must be included in the selected device list or there will be an error!
'''
from PlugLoad_Sim.inputstr_generator import make_input_generators, NameGenerator
from PlugLoad_Sim.goody import input_int, input_str, input_str_with_nummap
from PlugLoad_Sim.device_sim import write_to_ifile, analyze_data
from APS_scheduler.Advanced_Power_Strip import AdvancedPowerStripT2
from PlugLoad_Sim.inputstr_generator import InputGenerator

import PlugLoad_Sim.device_parser as device_parser
from APS_scheduler.APS_State import APS2_State
 
 
# bug list
# 1. adds 60 minutes to the APS thing no matter yet
#       a. quick disgusting fix: just subtract 60 from whatever

OFF_STATE     = 'off'     # denotes which state consumes 0 power each state must be the same in all devices
DEFAULT_STATE = 'standby' # these 2 states must ALWAYS be denoted in the XML file for this program to work

YES_NO_INPUTS = {'yes', 'y', 'no', 'n'}

MENU_STR = '''MENU:
a: add a device
d: delete a device
p: print the devices you have
r: run the simulation
q: quit
'''

def convert_time(time: int, int_period: int):
    '''converts time in minutes to the time in int_periods which is measured in seconds
    ie  5 minutes = 60 int_periods when int_period = 5s'''
    
    return 60/int_period * time

def input_device_model(devices_data: {dict}, p_string: str)->list:
    if type(devices_data) == set:
        z = zip(range(1, len(devices_data)+1), devices_data)
        inp = input_str_with_nummap('Which type of {} device do you want to choose? {}'.format(p_string, 
                    sorted(z)), devices_data)
        print('selected: {}'.format(inp))
        return [inp]
    else:
        keys_set = set(devices_data.keys())
        z = zip(range(1, len(keys_set)+1), keys_set)
        
        inp = input_str_with_nummap('Which type of {} device do you want to choose? {}'.format(
                                    p_string, sorted(z)), keys_set)
        
        p_string += '{}:'.format(inp)
        to_return = [inp]
        print('selected: {}'.format(inp))
        to_return.extend(input_device_model(devices_data[inp], p_string))
            
        return to_return

def create_ig_map(ig_list: list):
    return {d.dev_name: d for d in ig_list}

def get_unbound_devices(ig_map: dict, aps):
    return set(filter(lambda x: not x in aps.slave_devices() and x != aps.master_device() and x != 'aps',
                             ig_map.keys()))

def get_states(ig_map, devices: {str}):
    '''
    takes in a list of devices and asks user whether or not that device is being used
    returns a map that specifies what state each device is in
    '''
    result = {}
    
    for d in devices:
        inp = input_str('Are you using the {} [yes/no]: '.format(d), {'yes', 'y', 'no', 'n'})
        if inp.lower() in ['yes', 'y']:
            rlen = range(1, len(ig_map[d].states())+1)
            str_rlen = set(str(x) for x in rlen)
            state = input_str('Which of the following states is it in {}: '.format(
                              sorted(zip(rlen, ig_map[d].states()))), valid=ig_map[d].states().union(str_rlen))
            
            input_dict = dict(zip(rlen, ig_map[d].states()))
            if not state in ig_map[d].states():
                state = input_dict[int(state)]
            result[d] = state
        elif inp.lower() in ['no', 'n']:
            result[d] = DEFAULT_STATE
            
    return result

def write_on_states(dev_state_map: {str}, ig_map, n_periods):
    for dev, state in dev_state_map.items():
        ig_map[dev].write_on_state(state, n_periods)
        
def ig_write_from_iterable(device, iterable, ig_map, current_state, save_state = OFF_STATE):
    '''
    writes onto the ig_map from an iterable containing states and times spent in each state
    '''
    for state, time in iterable:
        if state != APS2_State.POWER_SAVE:
            ig_map[device].write_on_state(current_state, time)
        else:
            ig_map[device].write_on_state(save_state, time)
            
def ig_write_dep_devices(dev_state: dict, ig_map, aps_state_times):
    print(dev_state)
    for device, state in dev_state.items():
        ig_write_from_iterable(device, aps_state_times, ig_map, state)


def input_unbound_devices(ig_map, unbound_devices: {str}, time: int):
    dev_state = get_states(ig_map, unbound_devices)
    write_on_states(dev_state, ig_map, time)

def input_aps_devices(ig_map, aps, n_periods_IR, n_periods_move_IR, n_periods, int_period,start_state_time= None):
    master_state = get_states(ig_map, {aps.master_device()})
    
    # APS T1
    if master_state[aps.master_device()] == DEFAULT_STATE or master_state[aps.master_device()] == OFF_STATE:
        write_on_states(master_state, ig_map, n_periods)
        write_on_states(dict((dev, OFF_STATE) for dev in aps.slave_devices()), ig_map, n_periods)
        return
    
    dep_dev_states = get_states(ig_map, aps.slave_devices())
    # APS T2
    if start_state_time == None:
        apsState = APS2_State(aps, n_periods_IR, n_periods_move_IR, n_periods)
    else:
        apsState = APS2_State(aps, n_periods_IR, n_periods_move_IR, n_periods, 
                              start_state=start_state_time[0], start_periods=start_state_time[1])

    while(apsState.time_left() > 0):
        if apsState.check_state() == APS2_State.IR:
            ans = input_str('has there been IR in the last {}? '.format(aps.time_IR_only()))
            if ans.lower() in {'y', 'yes'}:
                time_sig    = input_int('How long ago?')
                sig_periods = n_periods_IR - int(convert_time(time_sig, int_period))
                apsState.input_signal(sig_periods)
            else:
                apsState.next_state()
        elif apsState.check_state() == APS2_State.IR_AND_MOVE:
            ans = input_str('has there been IR/movement in the last {}? '.format(aps.time_IR_and_movement()))
            if ans.lower() in {'y', 'yes'}:
                time_sig    = input_int('How long ago?')
                sig_periods = n_periods_move_IR - int(convert_time(time_sig, int_period))
                apsState.input_signal(sig_periods)
            else:
                apsState.next_state()
        elif apsState.check_state() == APS2_State.POWER_SAVE:
            apsState.next_state()
    
    state_times, carry_over = apsState.flush()
    
    ig_write_dep_devices(dep_dev_states, ig_map, state_times)
    ig_write_from_iterable(aps.master_device(), state_times, ig_map, master_state[aps.master_device()], save_state=DEFAULT_STATE)
    
    return carry_over
                
def input_at_interval(ig_map: ['InputGenerator'], time_info: tuple, unbound_devices: {str}, aps: AdvancedPowerStripT2, start_state_time = None):
    '''helper function for running the simulation, at each time interval it asks whether or not the
    device is being used then uses the writes'''
    
    ### this function is a mess refactor it into several functions at some point
    n_periods, n_periods_IR, n_periods_move_IR, int_period = time_info
    
    ### inputting unbound devices is the same case as inputting devices from the PlugLoadSim
    input_unbound_devices(ig_map, unbound_devices, n_periods)
    
    ### inputting aps_devices works a bit more differently where a APS_State Class will keep track of what
    ### state the aps is in in order for the 
    to_return = input_aps_devices(ig_map, aps, n_periods_IR, n_periods_move_IR, n_periods, int_period)
    return to_return

def run_sim(integration_period: int, input_generators: dict, aps: AdvancedPowerStripT2):
    '''runs the simulation that creates the input csv'''
    print('\nInput the start states:')  
    unbound_devices = get_unbound_devices(input_generators, aps)
  
    input_at_interval(input_generators, (1,10,10,integration_period), unbound_devices, aps)
    start_state_time = None
    
    while True:
        print()
        time_interval = input_int('How long is this time interval (in minutes)[enter 0 to end the simulation]: ')
        if time_interval == 0:
            break
        
        num_periods_interval = int(convert_time(time_interval, integration_period))
        num_periods_IR       = int(convert_time(aps.time_IR_only(), integration_period)) 
        num_periods_IRmove   = int(convert_time(aps.time_IR_and_movement(), integration_period)) 
        
        time_info = (num_periods_interval, num_periods_IR, num_periods_IRmove, integration_period)
        
        start_state_time = input_at_interval(input_generators, time_info, unbound_devices, aps, start_state_time)

def main():
    name_gen = NameGenerator()
    device_map = {}
    tree = device_parser.parse_data('../xmls/data_grouped.xml')
    devices_data = device_parser.parse_groupings(tree) # could become a bottleneck if xmls get large enough
    aps = None
    
    while True:
        inp = input_str(MENU_STR, valid={'a', 'p', 'r', 'q', 'd'})
        print()
        if inp == 'a':
            dev_key = input_device_model(devices_data, '')
            key,value = device_parser.search_data(tree, dev_key)
            device_map[name_gen.generate_name(key)] = value
        if inp == 'd':
            valid = set(device_map.keys())
            if len(valid) > 0:
                to_delete = input_str('Which device do you want to delete? {}: '.format(valid), valid)
                del device_map[to_delete]
            else:
                print('There are no devices to delete\n')
        if inp == 'p':
            print(set(device_map.keys()))
        if inp == 'c':
            pass
        if inp == 'r':
            input_generators = create_ig_map(make_input_generators(device_map))
            aps = AdvancedPowerStripT2('LG LED HiDef TV', ['Microsoft Xbox One', 'Dolby Surround Sound'], 60, move_time=75, is_on=False)

            integration_period = input_int('Enter integration period: ')
            run_sim(integration_period, input_generators, aps)
            
            device_map['aps'] = {'on': 1.5, 'off': 0.0}

            #write_to_ifile('csvs/test_APS.csv', integration_period, list(input_generators.values()))
            #analyze_data('csvs/test_APS.csv', integration_period, device_map)
            
            write_to_ifile('../csvs/test_APS.csv', integration_period, list(input_generators.values()))
            analyze_data('../csvs/test_APS.csv', integration_period, device_map)
        print()
        if inp == 'q':
            return
        
if __name__ == '__main__':
    main()
