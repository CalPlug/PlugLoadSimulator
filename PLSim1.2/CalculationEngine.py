from device_sim import write_to_ifile, write_to_peramfile, read_from_peramfile, analyze_data
import pickle

def main():
    integ_periods_file = open('integ_periods', 'rb')
    integ_periods_pickle = pickle.load(integ_periods_file)         # load file content in periods
    integ_periods_file.close() 
    
    #Unpickle device_map
    devicemp_file = open('devicemp', 'rb')
    devicemap_pickle = pickle.load(devicemp_file)         # load file content in generators
    devicemp_file.close()   
    
    analyze_data('csvs/test_group.csv', integ_periods_pickle, devicemap_pickle)

if __name__ == '__main__':
    main()