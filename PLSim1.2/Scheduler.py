from inputstr_generator import make_input_generators, NameGenerator
from goody import input_int, input_str
from device_sim import write_to_ifile, write_to_peramfile, read_from_peramfile, analyze_data
import pickle
import device_parser

# TODO
# -start setting up that way we can simulate multiple environments and make comparisons
#    + make it so that way one can rename a device (maybe do this automatically if there are multiple devices with the same model)
#    + start by creating a class to represent a simulation this contains the associated CSV, and device map


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
    '''helper function for running the simulation'''
    for inp_gen in ig_list:
        inp = input_str('Are you using the {} [yes/no]: '.format(inp_gen.dev_name), {'yes', 'y', 'no', 'n'})
        if inp.lower() in ['yes', 'y']:
            rlen = range(1, len(inp_gen.states())+1)
            str_rlen = set(str(x) for x in rlen)
            state = input_str('Which of the following states is it in {}: '.format(
                              sorted(zip(rlen, inp_gen.states()))), valid=inp_gen.states().union(str_rlen))
            
            input_dict = dict(zip(rlen, inp_gen.states()))
            if not state in inp_gen.states():
                state = input_dict[int(state)]
                
            inp_gen.write_on_state(state, time_interval)
        elif inp.lower() in ['no', 'n']:
            inp_gen.write_on_state('off', time_interval)

def run_sim(integration_period: int, input_generators: list):
    '''runs the simulation that creates the input csv'''
    print('\nInput the start states:')    
    input_at_interval(input_generators, 1)
    while True:
        print()
        time_interval = input_int('How long is this time interval (in minutes)[enter 0 to end the simulation]: ')
        if time_interval == 0:
            break
        
        num_periods_interval = int(convert_time(time_interval, integration_period))
        input_at_interval(input_generators, num_periods_interval)

def main():
    name_gen = NameGenerator()
    device_map = {}
#     tree = device_parser.parse_data('xmls/PLSim2Format.xml')
#    NewDevices.xml use to test backwards compatibility
    tree = device_parser.parse_data('xmls/NewDevices.xml')
    devices_data = device_parser.parse_groupings(tree)
    
    while True:
        inp = input_str(MENU_STR, valid={'a', 'p', 'r', 'q', 'd','g'})
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
        if inp == 'r':
            input_generators = make_input_generators(device_map)
            integration_period = input_int('Enter integration period: ')
            run_sim(integration_period, input_generators)
            
            #Pickling integration_period
            integ_periods_file = open('integ_periods','wb')
            pickle.dump(integration_period, integ_periods_file)
            integ_periods_file.close()
                                
            #Pickling device_map
            devicemp_file = open('devicemp','wb')
            pickle.dump(device_map, devicemp_file)
            devicemp_file.close()
            
            write_to_ifile('csvs/test_group.csv', integration_period, input_generators)
            
            write_to_peramfile('csvs/run_perams.cfg', integration_period, device_map)
            
            print ("CSV File Input Gen:")
            print(input_generators)
            print ("Integration Period:")
            print(integration_period)
            print ("Device Map:")
            print(device_map)
        
        print()
        
        if inp == 'q':
            return

main()