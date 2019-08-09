'''generate test Inputs'''
from random import randrange

def make_str_array(size, start_value=''):
    to_return = []
    for i in range(size):
        to_return.append(start_value)
    return to_return

def generate_valid_istring(num_states: int, size: int)->[str]:
    curr_size = 0
    to_return = make_str_array(num_states)
    
    while(curr_size < size):
        
        rand_index = randrange(num_states)
        
        isl_len = randrange(0, 300) + randrange(0, 300)
        isl_len = min(isl_len, size-curr_size)
        
        curr_size += isl_len
        
        to_return[rand_index] += isl_len * '1'
        for i in range(num_states):
            if i != rand_index:
                to_return[i] += isl_len * '0'
            
    return to_return

def generate_test_input(device_map: dict, size: int, file_name='test_input.csv'):
    with open(file_name, 'w') as outfile:
        outfile.write(generate_test_str(device_map, size))
    

def generate_test_str(device_map: dict, size: int):
    template_string = '{},{},{}'
    to_return = ''
        
    for k, v in device_map.items():
        i_string = generate_valid_istring(len(v.keys()), size)
        for i,j in zip(v.items(), i_string):
            k1,v1 = i
            to_return += template_string.format(k, k1, j) + '\n'
            
    return to_return
    

if __name__ == '__main__':
    pass
    #test stuff later
            