# BLE_log_data_extractor
SCRIPT_VERSION = '1.0'

import os
import aux_lib.common_BLE_aux_lib as common_BLE_aux_lib


#================================================================================================================
# setup:


# Log files must have ".txt" extensions.
BASE_PATH = './'
LOG_FOLDER = BASE_PATH + 'scan_log_2/'
RESULT_PATH = BASE_PATH + 'log_data_extractor_res.txt'


##PHRASE_TO_FIND = "\\x01\\x04"
PHRASE_TO_FIND = "C8:37:CF"


#================================================================================================================
# functions:


def print_res(tx):
    print(tx)
    if res_file:
        res_file.write(tx + '\n')


#================================================================================================================
# work:


print('SCRIPT START')
print('\n' * 2)

res_file = open(RESULT_PATH, 'w')

print_res('BLE_log_data_extractor v. ' + SCRIPT_VERSION)
print_res('PHRASE_TO_FIND: ' + PHRASE_TO_FIND)
print_res('\n' * 2)

log_file_path_list = common_BLE_aux_lib._get_log_path_list(LOG_FOLDER, '.TXT')
for log_file_path in log_file_path_list:
    print_res('log_file_path = ' + str(log_file_path))
    f = open(log_file_path, mode='r', encoding='utf-8')
    lines_list = f.readlines()
    f.close()
    i = 0
    for line in lines_list:
        if PHRASE_TO_FIND in line:
            print_res('[' + str(i) + '] ' + line)
            i += 1
    print_res('\n' * 2)

res_file.close()

print('\n' * 2)
print('SCRIPT STOP')


#================================================================================================================



