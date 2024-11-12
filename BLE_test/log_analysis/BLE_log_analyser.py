# BLE_log_analyser
SCRIPT_VERSION = '1.10'

import os
import aux_lib.common_BLE_aux_lib as common_BLE_aux_lib


#================================================================================================================
# setup:


# Log files must have ".txt" extensions.

BASE_PATH = './'

LOG_FOLDER_1 = BASE_PATH + 'scan_log_1/'
LOG_FOLDER_2 = BASE_PATH + 'scan_log_2/'
RESULT_PATH = BASE_PATH + 'log_analyser_res.txt'
RESULT_LIMIT = 10


#================================================================================================================
# functions:


def data_analyser(data_set_1, data_set_2, data_name_str):
    print_res('\n\n=========================================')
    print_res('common part of two ' + data_name_str + ' sets:')
    print_res('\n')
    common_part_data_set = set([el for el in data_set_1 if el in data_set_2])
    i = 1
    for data in common_part_data_set:
        if i <= RESULT_LIMIT:
            print_res(str(i) + ') ' + data)
            i += 1
        else:
            print_res('AND ' + str(len(common_part_data_set) - RESULT_LIMIT) + ' MORE...')
            break
    print_res('\n\n-----------------------------------------')
    print_res(data_name_str + ' -> data_set_1 - data_set_2:')
    print_res('\n')
    diff_dat_set = set([el for el in data_set_1 if el not in data_set_2])
    i = 1
    for data in diff_dat_set:
        if i <= RESULT_LIMIT:
            print_res(str(i) + ') ' + data)
            i += 1
        else:
            print_res('AND ' + str(len(diff_dat_set) - RESULT_LIMIT) + ' MORE...')
            break


#----------------------------------------------------------------------------------------------------------------


def get_field_set_from_BLE_scanner_logs(root_folder, extension):
    log_file_path_list = common_BLE_aux_lib._get_log_path_list(root_folder, extension)
    res_list = []
    for log_file_path in log_file_path_list:
        print_res('get_field_set_from_BLE_scanner_logs: ' + log_file_path)
        f = open(log_file_path, mode='r', encoding='utf-8')
        lines_list = f.readlines()
        f.close()
        for line in lines_list:
            field_list = [s.split('=>')[0].strip() for s in line.split(', ')]
            res_list += field_list
    return list(set(res_list))


def print_res(tx):
    print(tx)
    if res_file:
        res_file.write(tx + '\n')


#================================================================================================================
# work:


print('SCRIPT START')
print('\n' * 2)

res_file = open(RESULT_PATH, 'w')

print_res('field_set_1 FROM:')
field_set_1 = get_field_set_from_BLE_scanner_logs(LOG_FOLDER_1, '.TXT')
print_res('field_set_2 FROM:')
field_set_2 = get_field_set_from_BLE_scanner_logs(LOG_FOLDER_2, '.TXT')

mac_address_set_1 = common_BLE_aux_lib.get_mac_address_set(field_set_1)
mac_address_set_2 = common_BLE_aux_lib.get_mac_address_set(field_set_2)
data_analyser(mac_address_set_1, mac_address_set_2, 'mac_address')

manufacturer_data_set_1 = common_BLE_aux_lib.get_manufacturer_data_set(field_set_1)
manufacturer_data_set_2 = common_BLE_aux_lib.get_manufacturer_data_set(field_set_2)
data_analyser(manufacturer_data_set_1, manufacturer_data_set_2, 'manufacturer_data')

service_uuids_set_1 = common_BLE_aux_lib.get_service_uuids_set(field_set_1)
service_uuids_set_2 = common_BLE_aux_lib.get_service_uuids_set(field_set_2)
data_analyser(service_uuids_set_1, service_uuids_set_2, 'service_uuids')

service_data_set_1 = common_BLE_aux_lib.get_service_data_set(field_set_1)
service_data_set_2 = common_BLE_aux_lib.get_service_data_set(field_set_2)
data_analyser(service_data_set_1, service_data_set_2, 'service_data')

local_name_set_1 = common_BLE_aux_lib.get_local_name_set(field_set_1)
local_name_set_2 = common_BLE_aux_lib.get_local_name_set(field_set_2)
data_analyser(local_name_set_1, local_name_set_2, 'local_name')

res_file.close()

print('\n' * 2)
print('SCRIPT STOP')


#================================================================================================================



