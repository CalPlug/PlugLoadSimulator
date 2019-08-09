''' This module parses through XML file and creates a an instance of a Device
    class Device has 2 fields. a name and a map representing states and how much
    power they use. XML files follows this template:
    
    it specifically parses through AV devices
    
        <device = name>
            [<state: name, power>
            <\state>]
        \<device>
'''

import xml.etree.ElementTree as ET
from collections import defaultdict
from random import random
        
def parse_data(xml: str)->ET:
    tree = ET.parse(xml)
    root = tree.getroot()
    return root

def search_data(tree: ET, search_info:list, device_name = '', override=False)->dict:
    if len(search_info) == 0:
        #print(device_name)
        return build_device(tree, device_name, override = True)
    else:
        for child in tree:
            if child.get('name') == search_info[0]:
                if(len(search_info) <= 2 and not override):
                    device_name += ' ' + search_info[0].strip()
                return search_data(child, search_info[1:], device_name, override)

def adjust_data(tree:ET):
    if tree.tag == 'device-model':
        for child in tree:
            if not child.text == '':
                child.set('power', child.text)
                child.text = ''
                child.set('power_factor', str(round(random()/2,2)))
                child.set('thd', str(round(random()/2,2)))
    else:
        for child in tree:
            adjust_data(child)
            
def parse_groupings(tree: ET)->{dict: dict}:
    '''creates a nested dictionary that contains all the tags and their names while retaining their
    structure, used to list out the all the devices'''
    if tree.tag == 'device-model':
        return {tree.get('name')}
    elif tree.tag == 'data':
        to_return = defaultdict(dict)
        for child in tree:
            to_return.update(parse_groupings(child))
        return dict(to_return)
    else:
        to_return = {}
        for child in tree:
            if (tree.get('name')) in to_return:
                to_return[tree.get('name')].update(parse_groupings(child))
            else:
                to_return[tree.get('name')] = parse_groupings(child)
        return to_return

def build_device(tree: ET, device_name_n = '', override = False):
    device_name = tree.get('name')
    if override:
        device_name = device_name_n.strip()
    
    device_states = {}
    for child in tree:
        #device_states[child.get('name')] = int(child.text)
        device_states[child.get('name')] = float(child.get('power'))  #updated to float
    return (device_name, device_states)

def build_device_simple(tree: ET, device_name_n = '', override = False):
    device_name = tree.get('name')
    if override:
        device_name = device_name_n.strip()
    
    device_states = {}
    for child in tree:
        device_states[child.get('name')] = int(child.text)
    return (device_name, device_states)

def build_device_map(tree: ET)->dict:
    to_return = {}
    
    for child in tree:
        device = build_device_simple(child)
        to_return[device[0]] = device[1]
        
    return to_return


if __name__ == '__main__':
    to_parse = parse_data('data_grouped.xml')
    pg = parse_groupings(to_parse)
    d = search_data(to_parse, ['AV', 'television', 'Samsung', 'LCD SD TV'])
    print(pg)
    print(d)
#     adjust_data(to_parse)
#     with open('data_grouped.xml', 'w') as outfile:
#         outfile.write(ET.tostring(to_parse).decode())


            