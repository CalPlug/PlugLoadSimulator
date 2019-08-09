from schedulerlib.input import make_input_generators, NameGenerator, input_int, input_str
from schedulerlib.write import write_to_ifile, write_to_peramfile
from schedulerlib.parser import parse_data,parse_groupings,search_data,reorder_tree
from pprint import pprint
import pickle
import sys
from pathlib import Path
import csv

#***NOTICE:: Run through project "PLSim 1.2" as the set relative location within the entire project. 
#            Accordingly if this is run in a new project each input and output file may need to have 
#            a modified file path corresponding to this new file structure ***

# input files
#INPUT_XML = "simulationfiles/devicedatabases/xmls/PLSim2Format.xml" #This is the input power usage "database" format
INPUT_XML = 'simulationfiles/devicedatabases/xmls/DeviceListDB7.27.19.xml' #"simulationfiles/devicedatabases/xmls/DeviceList_xml.xml"

# output files
OUTPUT_PICKLE = 'run_params' #this is the pickled object file passed with the selected device list onto the calculation engine
OUTPUT_CONFIG = 'run_perams.cfg' #This is the list of parameters for the scheduler run, similar in content to the PICKLE file.
OUTPUT_CSV = 'test_group.csv' #This is the generated schedule for device operation
batch_file = "simulationfiles/batchfiles/batch_file_test.csv"

MENU_STR = '''Simulation Builder/Scheduler Main Menu:
a: Add a device to simulation
b: Run Batch from CSV
d: Delete a from simulation
p: Print current devices in simulation
r: Run scheduler on selected devices, display output, Quit
q: Quit simulation
'''

def input_device_model(devices_data: {dict}, p_string: str, batch_input: list, batch_input_index: int)->list:
    if type(devices_data) == set:
        print("device_model_if")
        z = zip(range(1, len(devices_data)+1), sorted(devices_data))
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        print('Which type of {} device do you want to choose? {}: '.format(p_string,
                        sorted(z)))
        input_dict = dict(zip(range(1, len(devices_data)+1), sorted(devices_data)))
        inp = batch_input[batch_input_index]
        print("---_______xxxx__________---")
        print("My INPUT: " + str(inp))
        if not inp in devices_data:
            inp = input_dict[int(inp)]
            
        print('selected: {}'.format(inp))
        return [inp]
    else:
        print("device_model_else")
        keys_set = set(devices_data.keys())
        z = zip(range(1, len(keys_set)+1), sorted(keys_set))
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        print(str_range)
        print('Which type of {} device do you want to choose? {}: '.format(p_string,
                        sorted(z)))
        inp = batch_input[batch_input_index]
        print("---_____________________---")
        print("My INPUT: " + str(inp))
       
        input_dict = dict(zip(range(1, len(keys_set)+1), sorted(keys_set)))
        print(input_dict)
        
        if not inp in keys_set:
            inp = input_dict[int(inp)]
        
        p_string += '{}:'.format(inp)
        print(p_string)
       
        to_return = [inp]
        print(to_return)
        print('selected: {}'.format(inp))
        #exit()
        to_return.extend(input_device_model(devices_data[inp], p_string, batch_input, (batch_input_index+1)))
            
        return to_return

def input_at_interval(ig_list: ['InputGenerator'], time_interval: int):
    '''helper function for running the simulation'''
    for inp_gen in ig_list:
        rlen = range(1, len(inp_gen.states())+1)
        str_rlen = set(str(x) for x in rlen)
        state = input_str('Which of the following states is \"{}\" in {}: '.format(inp_gen.dev_name,\
                          sorted(zip(rlen, sorted(inp_gen.states())))), valid=inp_gen.states().union(str_rlen))

        input_dict = dict(zip(rlen, sorted(inp_gen.states())))
        if not state in sorted(inp_gen.states()):
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

def run_sim_state(integration_period: int, input_generators: list, batch_input: list, batch_input_index: int, numOfStates: int):
    sindex = 0
    interval_sum = 0
    while True:
        for inp_gen in input_generators:
            rlen = range(1, len(inp_gen.states())+1)
            str_rlen = set(str(x) for x in rlen)
            print('Which of the following states is \"{}\" in {}[enter 0 to end the simulation]: '.format(inp_gen.dev_name,\
                                sorted(zip(rlen, sorted(inp_gen.states())))))
            state = batch_input[batch_input_index]
            print("The State is: " + str(state))
            sindex = sindex + 1
            if state == '0':
                return
            input_dict = dict(zip(rlen, sorted(inp_gen.states())))
            if not state in sorted(inp_gen.states()):
                state = input_dict[int(state)]
            if(sindex < numOfStates):
                print('How long is this time interval (in minutes)[enter 0 to end the simulation]: ')
                time_interval = int(batch_input[batch_input_index+1])
                interval_sum = time_interval + interval_sum
                print("The Time interval is " + str(time_interval))
            if(sindex == numOfStates):
                time_inverval = 1440 - interval_sum
                print("The Time interval is " + str(time_interval))
                num_periods_interval = int(60 / integration_period * time_interval)
                inp_gen.write_on_state(state, num_periods_interval)
                return 
            if time_interval == 0:
                return
            num_periods_interval = int(60 / integration_period * time_interval)
            inp_gen.write_on_state(state, num_periods_interval)
            batch_input_index = batch_input_index + 2

def getCSVBatch(filename:str)->list:
    list_of_profiles = []
    with open(filename) as f:
        reader = csv.reader(f,delimiter=',')
        for row in reader:
            print(row)
            list_of_profiles.append(row)
        

    print(list_of_profiles)
    #exit()
    return list_of_profiles


if "__main__" == __name__:

    # DUPLICATION CHECKS
    name_gen = NameGenerator()
    # key -> name of device "type brand model", value -> its data
    device_map = {}
    
    #Error Handling: File Exist
    file_location = INPUT_XML
    exist_flag = Path(file_location)
    if exist_flag.exists() == False :
        print("Error: XML file does not exist")
        print("Program Quit")
        sys.exit(1)
    
    #Error Handling: File Parsing
    try:
        # Parse xml
        tree = parse_data(file_location)
    except:
        print("Error: Unable to parse XML file")
        print("Program Quit")
        sys.exit(1);
    
    # All labels {class,type,brand,model} without any data
    devices_data = parse_groupings(tree)
    # devices_data = reorder_tree(devices_data)
    

    while True:
        inp = input_str(MENU_STR, valid={'a','b', 'd', 'p', 'r', 'q'}).lower()
        print()
        if inp == 'a':
            # dev_key[list of choice by steps]
            dev_key = input_device_model(devices_data, '')
            # key -> "type+brand+model", value -> power and etc
            key,value = search_data(tree, dev_key)
            # name_gen.generate_name checks DUPLICATES and add a number at the end if DUPLICATED
            device_map[name_gen.generate_name(key)] = value
        elif inp == 'b':
            # TODO: ASK FOR input filename and path
            print("DEVICE MAP")
            print(device_map)
            #exit()
            batch_csv_data = getCSVBatch(batch_file)
            batchNum = len(batch_csv_data)
            bindex = 0
            while(bindex < batchNum):
                print("Entering " + str(bindex) + " Profile")
                print(batch_csv_data)
                print("_________________________________")
                dev_key = input_device_model(devices_data, '', batch_csv_data[bindex], 1)
                print("DEV KEY")
                print(dev_key)
                #exit()
                # key -> "type+brand+model", value -> power and etc
                key,value = search_data(tree, dev_key)
                # name_gen.generate_name checks DUPLICATES and add a number at the end if DUPLICATED
                device_map[name_gen.generate_name(key)] = value
                print("______End Profile"+ str(bindex) + "_______")
                #bindex = bindex + 1
                input_generators = make_input_generators(device_map)
                print(input_generators)
                #exit()
                # Get Integration Period
                print('Enter integration period for simulation calculation framework (whole seconds): ')
                integration_period = int(batch_csv_data[bindex][5])
                print(integration_period)
                # Get Periods
                run_sim_state(integration_period, input_generators, batch_csv_data[bindex], 8,  int(batch_csv_data[bindex][7]))
                # run_sim(integration_period, input_generators)

                # pickle run_perams
                with open(('simulationfiles/scheduleobjects/'+str(batch_csv_data[bindex][0])+ OUTPUT_PICKLE),'wb') as fd:
                    pickle.dump({'integeration_period':integration_period,'device_map':device_map}, fd)

                # write info file
                write_to_ifile('simulationfiles/scheduleobjects/csvs/'+str(batch_csv_data[bindex][0])+OUTPUT_CSV, integration_period, input_generators)
                # write copy of the pickle file
                write_to_peramfile('simulationfiles/scheduleobjects/csvs/'+str(batch_csv_data[bindex][0]) +OUTPUT_CONFIG, integration_period, device_map)
                
                print("CSV File Input Gen:")
                print(input_generators)
                print("Integration Period:")
                print(integration_period)
                print("Device Map:")
                print(device_map)
                #exit()
                device_map = {}
                bindex = bindex + 1
            # Quit the Program after Simulation
            exit(0)

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
            integration_period = input_int('Enter integration period for simulation calculation framework (whole seconds): ')
            # Get Periods
            run_sim_state(integration_period, input_generators)
            # run_sim(integration_period, input_generators)

            # pickle run_perams
            with open('simulationfiles/scheduleobjects/' + OUTPUT_PICKLE,'w') as fd:
                pickle.dump({'integeration_period':integration_period,'device_map':device_map}, fd)

            # write info file
            write_to_ifile(OUTPUT_CSV, integration_period, input_generators)
            # write copy of the pickle file
            write_to_peramfile(OUTPUT_CONFIG, integration_period, device_map)
            
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
