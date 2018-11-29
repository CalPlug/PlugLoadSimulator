'''
Some functions that make life easier 

@author: Klint
'''


def input_str(prompt: str, valid = {})-> str:
    if len(valid) == 0:
        return input(prompt)
    else:
        inp = ''
        while not inp in valid:
            inp = input(prompt)
            if not inp in valid:
                print('Only the following inputs are allowed {}'.format(valid))
        return inp
    
def input_int(prompt: str, valid={}, error_message='Please enter a numerical input'):
    if len(valid) == 0:
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print(error_message)
    else:
        inp = ''
        while not inp in valid:
            while True:
                try:
                    inp = int(input(prompt))
                    break
                except ValueError:
                    print(error_message)
            if not inp in valid:
                print('Only the following inputs are allowed {}'.format(valid))
        return inp

def make_str_array(size, start_value=''):
    to_return = []
    for i in range(size):
        to_return.append(start_value)
    return to_return

def make_int_array(size, start_value=0):
    '''returns an int list of length size with values start_value, default being 0'''
    to_return = []
    for i in range(size):
        to_return.append(0)
    
    return to_return

if __name__ == '__main__':
    i1 = input_int('Enter a number: ', valid = {1,2,3,4})
    i2= input_str('Enter something')
    valid = ['yes', 'no', 'maybe']
    i3 = input_str('Enter something in {}: '.format(valid), valid)
    
    print(i1,i2,i3)
    