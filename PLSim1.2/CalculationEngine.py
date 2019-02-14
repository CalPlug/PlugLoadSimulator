from enginelib.graph import make_graph,make_power_graph,show_graph
from enginelib.write import write_to_csv
import csv
import pickle
import numpy as np
import sys
from pathlib import Path

# input files
INPUT_CSV = 'csvs/test_group.csv'
INPUT_PARAM = 'run_params'

# output files
OUTPUT_CSV = 'outputs/graph_file_test.csv'

# TODO: FAKE EXTENSION to coordinate with CONFIG FILE WHICH WILL BE PROVIDED TO TURN OR OFF FEATURES
ENABLED_LIST = ['power_factor','thdI', 'test']


def analyze_data(file_name: str, integration_period: int, device_map: dict):

    #Error Handling: File Exist
    file_location = file_name
    exist_flag = Path(file_location)
    if exist_flag.exists() == False :
        print("Error: CSV File does not exist")
        print("Program Quit")
        sys.exit(1)
    
    #Error Handling: File Parsing
    try:
        # {device_name:{cate:[np array of value]}}
        device_cate_map = parse_inputfile(file_name, device_map)
    except:
        print("Error: Unable to parse CSV file")
        print("Program Quit")
        sys.exit(1);

    # Total Power Array
    total_power_array = None
    for device in device_cate_map:
        total_power_array = device_cate_map[device]['power'] \
                        if total_power_array is None\
                        else total_power_array+device_cate_map[device]['power']

    # Integral Array, Energy Consumption Array
    integral_array = make_integral_array(total_power_array, integration_period)
    print('integral', integral_array)

    # Total Power and Total Energy
    make_graph(total_power_array, integration_period, 'Time (hr)', 'Power (W)', 'Total Power Consumed',1, sub=int(121))
    make_graph(integral_array, integration_period, 'Time (hr)', 'Energy (W*hr)', 'Total Energy Used',1, sub=int(122))

    # add up default power array
    graph_row = f'{1+len(ENABLED_LIST)}'
    graph_col = f'{len(device_cate_map)}'

    counter = 0
    for util in ['power']+ENABLED_LIST:
        for device_name in device_cate_map:
            counter += 1
            # to make sure only bottom graph has x label
            if counter <= int(graph_row)*int(graph_col)-len(device_cate_map):
                if util == 'power':
                    make_power_graph(device_cate_map[device_name][util], \
                               integration_period, \
                               '', \
                               util, \
                               f'{device_name} {util} Graph', \
                               2, \
                               sub=int(graph_row + graph_col + f'{counter}'))
                else:
                    make_graph(device_cate_map[device_name][util],\
                                integration_period,\
                                '',\
                                util,\
                                f'{device_name} {util} Graph',\
                                2,\
                                sub=int(graph_row+graph_col+f'{counter}'))
            else:
                make_graph(device_cate_map[device_name][util], \
                            integration_period, \
                            'Time (hr)', \
                            util, \
                            f'{device_name} {util} Graph', \
                            2, \
                            sub=int(graph_row + graph_col + f'{counter}'))

    # write to csv
    write_to_csv(OUTPUT_CSV,integration_period,device_cate_map)

    print('\nEnergy Used: ', integral_array[-1], 'Watt-hours')

    show_graph()

def parse_inputfile(file, device_map) -> dict:
    '''parses the device input file which is a csv file with format
    device, state, on/off string

    on/off string denotes with a 1 or a 0 whether or not a device is on during that time
    '''

    # initialize to_return
    to_return = {}
    categories = [cate for cate in device_map[list(device_map.keys())[0]][list(device_map[list(device_map.keys())[0]].keys())[0]]]
    devices = [device for device in list(device_map.keys())]
    for device in devices:
        to_return[device] = {}
    for device in to_return:
        for cate in categories:
            to_return[device][cate] = None

    with open(file, 'r') as i_file:
        # ignore sample rate line
        i_file.readline()
        # parse device_name,state,sequence
        for line in i_file:
            info = line.rstrip().split(',')
            device, state, i_string = info[0], info[1], info[2]

            # assign value based on value of Category and Sequence
            state_np = np.array(list(i_string), dtype=float)
            for cate in device_map[device][state]:
                to_return[device][cate] = state_np * device_map[device][state][cate] \
                    if to_return[device][cate] is None \
                    else to_return[device][cate] + state_np * device_map[device][state][cate]

    return to_return

def make_integral_array(power_array: list, integration_period: int):
    to_return = [0]
    for i in range(len(power_array)-1):
        to_return.append(energy_used(power_array[i:i+2], integration_period) + to_return[-1])
    return to_return

def energy_used(power_array, int_period: int):
    '''trapezoidal riemman sum estimate of the amount of power used'''
    return (sum(power_array[1:])/3600*int_period + sum(power_array[:len(power_array)-1])/3600*int_period)/2

def AttributesCheck(ENABLED_LIST, device_map):
    LIST_RETURN = []
    for a, device in enumerate(device_map):
        # print(device)
        for b, state in enumerate(device_map[device]):
            # print(state)
            for enabled in ENABLED_LIST:
                if enabled not in device_map[device][state]:
                    print(enabled + ' not found in ' + device + ' for ' + state + ' state')
                elif enabled not in LIST_RETURN:
                    LIST_RETURN.append(enabled)
            # for c, attributes in enumerate(state):
                
    return LIST_RETURN


if __name__ == '__main__':

    #Error Handling: File Exist
    file_location = INPUT_PARAM
    exist_flag = Path(file_location)
    if exist_flag.exists() == False :
        print("Error: Param File does not exist")
        print("Program Quit")
        sys.exit(1)

    #Error Handling: File Parsing
    try:
        # open pickle file to get parameters
        with open(INPUT_PARAM, 'rb') as param_fd:
            params = pickle.load(param_fd)
    except:
        print("Error: Unable to pickle objects")
        print("Program Quit") 
        sys.exit(1);


    ENABLED_LIST = AttributesCheck(ENABLED_LIST, params['device_map'])
    
    
    analyze_data(INPUT_CSV, params['integeration_period'], params['device_map'])
        
