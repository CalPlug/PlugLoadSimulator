from schedulerlib.input import make_input_generators, NameGenerator, input_int, input_str
from schedulerlib.write import write_to_ifile, write_to_peramfile
from schedulerlib.parser import parse_data,parse_groupings,search_data
from pprint import pprint
import pickle


MENU_STR = '''MENU:
a: Add a device
d: delete a device
p: print the devices you have
r: Run the simulation and Quit
q: Quit
'''

def input_device_model(devices_data: {dict}, p_string: str)->list:
    if type(devices_data) == set:
        z = zip(range(1, len(devices_data)+1), devices_data)
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        inp = input_str('Which type of {} device do you want to choose? {}: '.format(p_string,
                        sorted(z)), valid=devices_data.union(str_range))
        input_dict = dict(zip(range(1, len(devices_data)+1), devices_data))
        
        if not inp in devices_data:
            inp = input_dict[int(inp)]
            
        print('selected: {}'.format(inp))
        return [inp]
    else:
        keys_set = set(devices_data.keys())
        z = zip(range(1, len(keys_set)+1), keys_set)
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        inp = input_str('Which type of {} device do you want to choose? {}: '.format(p_string,
                        sorted(z)), valid=keys_set.union(str_range))
        
        input_dict = dict(zip(range(1, len(keys_set)+1), keys_set))
        
        if not inp in keys_set:
            inp = input_dict[int(inp)]
            
        p_string += '{}:'.format(inp)
        to_return = [inp]
        print('selected: {}'.format(inp))
        to_return.extend(input_device_model(devices_data[inp], p_string))
            
        return to_return

def input_at_interval(ig_list: ['InputGenerator'], time_interval: int):
    '''helper function for runniang the simulation'''
    for inp_gen in ig_list:
        rlen = range(1, len(inp_gen.states())+1)
        str_rlen = set(str(x) for x in rlen)
        state = input_str('Which of the following states is \"{}\" in {}: '.format(inp_gen.dev_name,\
                          sorted(zip(rlen, inp_gen.states()))), valid=inp_gen.states().union(str_rlen))

        input_dict = dict(zip(rlen, inp_gen.states()))
        if not state in inp_gen.states():
            state = input_dict[int(state)]

        inp_gen.write_on_state(state, time_interval)

def run_sim(integration_period: int, input_generators: list):
    '''runs the simulation that creates the input csv'''

    while True:
        print()
        time_interval = input_int('How long is this time interval (in minutes)[enter 0 to end the simulation]: ')
        if time_interval == 0:
            return
        num_periods_interval = int(60 / integration_period * time_interval)
        input_at_interval(input_generators, num_periods_interval)


if "__main__" == __name__:

    # DUPLICATION CHECKS
    name_gen = NameGenerator()
    # key -> name of device "type brand model", value -> its data
    device_map = {}

    # Parse xml
    tree = parse_data('xmls/PLSim2Format.xml')
    # All labels {class,type,brand,model} without any data
    devices_data = parse_groupings(tree)

    while True:
        inp = input_str(MENU_STR, valid={'a', 'd', 'p', 'r', 'q'}).lower()
        print()
        if inp == 'a':
            # dev_key[list of choice by steps]
            dev_key = input_device_model(devices_data, '')
            # key -> "type+brand+model", value -> power and etc
            key,value = search_data(tree, dev_key)
            # name_gen.generate_name checks DUPLICATES and add a number at the end if DUPLICATED
            device_map[name_gen.generate_name(key)] = value
        elif inp == 'd':
            valid = set(device_map.keys())
            if len(valid) > 0:
                to_delete = input_str('Which device do you want to delete? {}: '.format(valid), valid)
                del device_map[to_delete]
            else:
                print('There are no devices to delete\n')
        elif inp == 'p':
            pprint(device_map)
        elif inp == 'r':
            input_generators = make_input_generators(device_map)
            # Get Integration Period
            integration_period = input_int('Enter integration period: ')
            # Get Periods
            run_sim(integration_period, input_generators)

            # pickle run_perams
            with open('run_params','wb') as fd:
                pickle.dump({'integeration_period':integration_period,'device_map':device_map}, fd)

            # write info file
            write_to_ifile('csvs/test_group.csv', integration_period, input_generators)
            # write copy of the pickle file
            write_to_peramfile('csvs/run_perams.cfg', integration_period, device_map)
            
            print ("CSV File Input Gen:")
            print(input_generators)
            print ("Integration Period:")
            print(integration_period)
            print ("Device Map:")
            print(device_map)

            # Quit the Program after Simulation
            exit(0)

        elif inp == 'q':
            exit(0)

        print()