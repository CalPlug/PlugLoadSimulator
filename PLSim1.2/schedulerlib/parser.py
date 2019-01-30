''' This module parses through XML file and creates a an instance of a Device
    class Device has 2 fields. a name and a map representing states and how much
    power they use. XML files follows this template:
    
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
    
    root = parse_non_static_type(root)
#     print_states(root)
        
    return root

def parse_non_static_type(tree:ET):
    for a, deviceClass in enumerate(tree):
        for b, deviceType in enumerate(deviceClass):
            for c, deviceBrand in enumerate(deviceType):
                for d, deviceModel in enumerate(deviceBrand):
                    indexesToDelete = []
                    for e, state in enumerate(deviceModel):
                        if 'type' in state.attrib:
                            if state.get('type') != 'static':
                                indexesToDelete.append(e)
                    for index in reversed(indexesToDelete):
                        del tree[a][b][c][d][index]
                        
    return tree
    
def print_states(tree:ET):
    totalNumber = 1
    for deviceClass in tree:
        for deviceType in deviceClass:
            for deviceBrand in deviceType:
                for deviceModel in deviceBrand: 
                    for index, state in enumerate(deviceModel):
                        print(totalNumber, ': ', state.attrib)
                        totalNumber = totalNumber + 1
    return tree

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

def search_data(tree: ET, search_info:list, device_name = '', override=False)->dict:
    if len(search_info) == 0:
        return build_device(tree, device_name, override = True)
    else:
        for child in tree:
            if child.get('name') == search_info[0]:
                if(len(search_info) <= 3 and not override):
                    device_name += '|' + search_info[0].strip()
                    device_name = device_name.strip('|')
                return search_data(child, search_info[1:], device_name, override)

def build_device(tree: ET, device_name_n = '', override = False):
    device_name = tree.get('name')
    if override:
        device_name = device_name_n.strip()
    
    device_states = {}
    for state in tree:
        device_states[state.get('name')] = {}
        for key,value in state.items():
            if key != 'name' and key != 'type' and key != 'comments':
                device_states[state.get('name')][key] = float(value)

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
    to_parse = parse_data('xmls/PLSim2Format.xml')
    pg = parse_groupings(to_parse)
    d = search_data(to_parse, ['Entertainment Electronics','DVD Player', 'Samsung', 'Model XXXXXXXXX'])
    print(pg)
    print(d)
#     adjust_data(to_parse)
#     with open('data_grouped.xml', 'w') as outfile:
#         outfile.write(ET.tostring(to_parse).decode())

