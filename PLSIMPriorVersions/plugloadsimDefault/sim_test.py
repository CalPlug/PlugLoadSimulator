'''
Created on Feb 18, 2016

@author: Klint
'''
import unittest

from randtest_input_generator import generate_test_input
from inputstr_generator import InputGenerator
from goody import input_int
from device_sim import write_to_ifile, analyze_data, analyze_data_nograph
from stopwatch import Stopwatch

import device_parser
from _collections import OrderedDict


class Test(unittest.TestCase):


    def testName(self):
        pass

# def test3():
#     device_map = device_parser.build_device_map(device_parser.parse_data('test.xml'))
#     integration_period = input_int("integration factor (in seconds): ")   
#     input_generators = []
#      
#     for k,v in device_map.items():
#         input_generators.append(InputGenerator(k, set(v.keys())))
#          
#     run_sim(integration_period, input_generators)
#     write_to_ifile('test_input_manual.csv', integration_period, input_generators)
#     analyze_data('test_input_manual.csv', integration_period, device_map)
# 
# 
# def test2():
#     tree = device_parser.parse_data('data_grouped.xml')
#     devices_data = device_parser.parse_groupings(tree)
#     search_info = input_device_model(devices_data, 'class')
#     device = device_parser.search_data(tree, search_info)
#     print(device)
    
def test_largescale():
    s = Stopwatch()
    integration_factor = 5
    #device_map = device_parser.build_device_map(device_parser.parse_data('test.xml'))
    device_map = device_parser.build_device_map(device_parser.parse_data('xmls/data_grouped.xml'))
    test_size = 10000
    histogram = OrderedDict()
    
    for i in range(5):
        time = 0.0

        for j in range(5):
            s.start()
            generate_test_input(device_map, test_size, file_name='test_input1.csv')
            s.stop()
            print('Generating test input of size {}: '.format(test_size), s.read())
        
            s.reset()
            s.start()
            analyze_data_nograph('csvs/test_input1.csv', integration_factor, device_map)
            s.stop()
            print('Processing input of size {}:     '.format(test_size), s.read())

            time += s.read()
            s.reset()
            
        print('Average time for input of size {}:  '.format(test_size), time/5)
        histogram[test_size] = time/5
        
        test_size *= 2

    print(histogram)
    
    for i,j in histogram.items():
        print(' size | time ')
        print('{0:5d}|{1:5f}'.format(i,j))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    test_largescale()