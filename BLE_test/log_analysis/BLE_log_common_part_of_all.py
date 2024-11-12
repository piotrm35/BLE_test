# BLE_log_common_part_of_all
SCRIPT_VERSION = '1.2'

import os
import aux_lib.common_BLE_aux_lib as common_BLE_aux_lib


#================================================================================================================
# setup:


# Log files must have ".txt" extensions.

BASE_PATH = './'

LOG_FOLDER = BASE_PATH + 'scan_log_2/'
RESULT_PATH = BASE_PATH + 'log_common_part_of_all_res.txt'
RESULT_LIMIT = 10


#================================================================================================================
# functions:


def get_common_part_of_two(data_set_1, data_set_2):
    return set([el for el in data_set_1 if el in data_set_2])


#----------------------------------------------------------------------------------------------------------------


def get_field_set_from_BLE_scanner_log(log_file_path):
    res_list = []
##    print_res('get_field_set_from_BLE_scanner_log: ' + log_file_path)
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


def print_output_data_set(output_data_set, data_name_str):
    print_res('\n\n-----------------------------------------')
    print_res('common part of all ' + data_name_str + ' sets:')
    print_res('\n')
    i = 1
    for data in output_data_set:
        if i <= RESULT_LIMIT:
            print_res('(' + str(i) + ') -> ' + data)
            i += 1
        else:
            print_res('AND ' + str(len(output_data_set) - RESULT_LIMIT) + ' MORE...')
            break


#================================================================================================================
# work:


print('SCRIPT START')
print('\n' * 2)

res_file = open(RESULT_PATH, 'w')

log_file_path_list = common_BLE_aux_lib._get_log_path_list(LOG_FOLDER, '.TXT')
mac_address_set_1 = None
manufacturer_data_set_1 = None
service_uuids_set_1 = None
service_data_set_1 = None
local_name_set_1 = None
n = 0
for log_file_path in log_file_path_list:
    n += 1
    print_res('[' + str(n) + '/' + str(len(log_file_path_list)) + ']\tlog_file_path = ' + str(log_file_path))
    field_set = get_field_set_from_BLE_scanner_log(log_file_path)
    if mac_address_set_1 is None:
        mac_address_set_1 = common_BLE_aux_lib.get_mac_address_set(field_set)
        manufacturer_data_set_1 = common_BLE_aux_lib.get_manufacturer_data_set(field_set)
        service_uuids_set_1 = common_BLE_aux_lib.get_service_uuids_set(field_set)
        service_data_set_1 = common_BLE_aux_lib.get_service_data_set(field_set)
        local_name_set_1 = common_BLE_aux_lib.get_local_name_set(field_set)
    else:
        mac_address_set_2 = common_BLE_aux_lib.get_mac_address_set(field_set)
        manufacturer_data_set_2 = common_BLE_aux_lib.get_manufacturer_data_set(field_set)
        service_uuids_set_2 = common_BLE_aux_lib.get_service_uuids_set(field_set)
        service_data_set_2 = common_BLE_aux_lib.get_service_data_set(field_set)
        local_name_set_2 = common_BLE_aux_lib.get_local_name_set(field_set)

        mac_address_set_1 = get_common_part_of_two(mac_address_set_1, mac_address_set_2)
        manufacturer_data_set_1 = get_common_part_of_two(manufacturer_data_set_1, manufacturer_data_set_2)
        service_uuids_set_1 = get_common_part_of_two(service_uuids_set_1, service_uuids_set_2)
        service_data_set_1 = get_common_part_of_two(service_data_set_1, service_data_set_2)
        local_name_set_1 = get_common_part_of_two(local_name_set_1, local_name_set_2)

print_output_data_set(mac_address_set_1, 'mac_address')
print_output_data_set(manufacturer_data_set_1, 'manufacturer_data')
print_output_data_set(service_uuids_set_1, 'service_uuids')
print_output_data_set(service_data_set_1, 'service_data')
print_output_data_set(local_name_set_1, 'local_name')

res_file.close()

print('\n' * 2)
print('SCRIPT STOP')


#================================================================================================================



