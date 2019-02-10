
def write_to_csv(file_name, integration_period,device_cate_map):
    second_length = len(device_cate_map[list(device_cate_map.keys())[0]][list(device_cate_map[list(device_cate_map.keys())[0]].keys())[0]])
    time_array = str(list(range(0,second_length)))[1:-1]
    with open(file_name, 'w') as outfile:
        outfile.write(f'time,{time_array}\n')
        for device_name in device_cate_map:
            for cate in device_cate_map[device_name]:
                outfile.write(f'{device_name},{cate},{str(list(device_cate_map[device_name][cate]))[1:-1]}\n')