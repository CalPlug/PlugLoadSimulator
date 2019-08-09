'''
Input Generator class

@author: Klint
'''

def input_str(prompt: str, valid={}) -> str:
    if len(valid) == 0:
        return input(prompt)
    else:
        inp = ''
        while not inp in valid:
            inp = input(prompt)
            if inp == '0':
                return '0'
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

def make_input_generators(device_map: dict):
    input_generators = []
    
    for k,v in device_map.items():
        input_generators.append(InputGenerator(k, set(v.keys())))
    
    return input_generators

class InputGenerator:

    
    def __init__(self, device: str, states: set):
        
        self.dev_name = device
        self._dev_strdict = self._make_strdict(states)
        self._curr_time = 0
    
    def _make_strdict(self, states: set):
        to_return = {};
        for state in states:
            to_return[state] = ''
        return to_return
    
    def write_on_state(self, state: str, int_time: int):
#         time_left = self._max_size - self._curr_time
#         if int_time > time_left: # may throw error here idk yet
#             int_time = time_left
        
        for key in self._dev_strdict.keys():
            if key == state:
                self._dev_strdict[key] += int_time*'1'
            else:
                self._dev_strdict[key] += int_time*'0'
        
        self._curr_time += int_time
        
    def states(self):
        return set(self._dev_strdict.keys())
    
    def _build_str(self):
        template = '{},{},{}\n'
        to_return = ''
        
        for k,v in self._dev_strdict.items():
            to_return += template.format(self.dev_name, k, v)
        
        return to_return
    
    def generate_str(self):            
        return self._build_str()
    
    def __repr__(self):
        to_return  = 'curr_size: {}\n'.format(self._curr_time)
        to_return += self._build_str()
        return to_return

from collections import Counter

'''
Counter, d = {'a': 1, 'b':3}
d['a'] == 1
d['a'] += 11
d['a'] == 12

class NameGenerator:
    add_word(s: string)->increment the count of that word if it exists, otherwise set count = 0

    get_string(s: string)-> return s + count as string if 0, return s
    
    public void method(this, int x, int y)
        a = (this.a)
        method2 == (this.method2())
'''


class NameGenerator:
    '''
        Prevent Duplicates of Device Name
    '''
    
    def __init__(self):
        self.counter = Counter()
        
    def add_word(self, s):
        if s in self.counter:
            self.counter[s] += 1
        else:
            self.counter[s] = 0
    
    def generate_name(self, s):
        self.add_word(s)
        if self.counter[s] == 0:
            return s
        else:
            return s + ' ({})'.format(self.counter[s])
        
if __name__ == '__main__':
    i1 = InputGenerator('tv', {'on', 'off', 'standby'})
    
    i1.write_on_state('on', 25)
    print(i1)
    i1.write_on_state('off', 50)
    i1.write_on_state('standby', 25)
    
    i_str = i1.generate_str()
    print(i_str)
    
    n = NameGenerator()
    print(n.generate_name('a'))
    print(n.generate_name('a'))
    
    print(n.generate_name('b'))
    print(n.generate_name('b'))
    
    