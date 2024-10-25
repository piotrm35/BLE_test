# BLE_test
SCRIPT_VERSION = '2.0'


import os
import time
import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import log_analysis.aux_lib.common_BLE_aux_lib as common_BLE_aux_lib


#==============================================================================================================================================================================================================================


SCANNER_MODE = 'P'  # P -> passive; A -> active
BASE_PATH = './'


devices_dict = {}
first_dev_log_time_list = []
first_dev_log_idx = 1
total_number_logs_dict = {}
FIRST_DEV_LOG_MAX_DELAY = 7
MAX_UNIQUE_KEY_IDX = 5
TOTAL_NUMBER_DEV_LOGS_CHANGE_FILE_PERIOD = 1 * 60
SCAN_LOOP_DELAY = 3.0
last_total_number_dev_logs_change_timestamp = time.time()
script_start_datetime_str = None


def simple_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    global first_dev_log_idx
    advertisement_data_str = str(advertisement_data)
    advertisement_data_str = get_normalized_advertisement_data_str(advertisement_data_str)
    device_name = str(device.name).replace('None', '-')
    if not device_name.strip():
        device_name = '-'
    known_name = '-'
    if device.address in list(common_BLE_aux_lib.DEV_ADDRESS_MAP.keys()):
        known_name = ':' + common_BLE_aux_lib.DEV_ADDRESS_MAP[device.address] + ':'
    else:
        known_name = common_BLE_aux_lib.get_known_name_from_advertisement_data_match(advertisement_data_str)
    advertisement_data_str = common_BLE_aux_lib.add_uuid_description_to_advertisement_data_str(advertisement_data_str)
    if device.address not in first_dev_log_time_list:
        f = open(FIRST_DEV_LOG_TIME_FILE_PATH, 'a')
        f.write(
                str(first_dev_log_idx) + ') ' +
                common_BLE_aux_lib.get_current_time_str() + ' -> ' +
                device.address + ', ' +
                common_BLE_aux_lib.get_mac_address_type(device.address) + ', ' +
                str(device.rssi) + ', ' +
                device_name + ', ' +
                known_name + ', ' +
                advertisement_data_str +
                '\n'
            )
        f.close()
        first_dev_log_idx += 1
        first_dev_log_time_list.append(device.address)
    total_number_logs_dict_keys = list(total_number_logs_dict.keys())
    if device.address not in total_number_logs_dict_keys:
        total_number_logs_dict[device.address] = {
                'max_RSSI': device.rssi,
                'first_log_datatime': common_BLE_aux_lib.get_current_datetime_str(),
                'last_log_datetime': common_BLE_aux_lib.get_current_datetime_str(),
                'log_count': 1,
                'device_name': device_name,
                'known_name': known_name,
                'advertisement_data': advertisement_data_str
            }
    else:
        if total_number_logs_dict[device.address]['max_RSSI'] < device.rssi:
            total_number_logs_dict[device.address]['max_RSSI'] = device.rssi
        total_number_logs_dict[device.address]['log_count'] += 1
        if total_number_logs_dict[device.address]['device_name'] == '-':
            total_number_logs_dict[device.address]['device_name'] = device_name
        if len(total_number_logs_dict[device.address]['known_name']) < len(known_name):
            total_number_logs_dict[device.address]['known_name'] = known_name
        total_number_logs_dict[device.address]['last_log_datetime'] = common_BLE_aux_lib.get_current_datetime_str()
        stored_advertisement_data_dict = common_BLE_aux_lib.get_advertisement_data_dict(total_number_logs_dict[device.address]['advertisement_data'])
        stored_advertisement_data_dict_keys = list(stored_advertisement_data_dict.keys())
        stored_advertisement_data_dict_values = list(stored_advertisement_data_dict.values())
        new_advertisement_data_dict = common_BLE_aux_lib.get_advertisement_data_dict(advertisement_data_str)
        new_advertisement_data_dict_keys = list(new_advertisement_data_dict.keys())
        for new_advertisement_data_dict_key in new_advertisement_data_dict_keys:
            if new_advertisement_data_dict[new_advertisement_data_dict_key] not in stored_advertisement_data_dict_values:
                unique_key_idx = get_unique_key_idx_in_list(new_advertisement_data_dict_key, stored_advertisement_data_dict_keys)
                if unique_key_idx <= MAX_UNIQUE_KEY_IDX:
                    if unique_key_idx == 0:
                        total_number_logs_dict[device.address]['advertisement_data'] += ', ' + new_advertisement_data_dict_key + '=' + new_advertisement_data_dict[new_advertisement_data_dict_key]
                    elif unique_key_idx == MAX_UNIQUE_KEY_IDX:
                        total_number_logs_dict[device.address]['advertisement_data'] += ', ' + new_advertisement_data_dict_key + '_MAX_UNIQUE_KEY_IDX=' + new_advertisement_data_dict[new_advertisement_data_dict_key]
                    else:
                        total_number_logs_dict[device.address]['advertisement_data'] += ', ' + new_advertisement_data_dict_key + '_' + str(unique_key_idx) + '=' + new_advertisement_data_dict[new_advertisement_data_dict_key]
    devices_dict[device.address] = {
            'RSSI': device.rssi,
            'device_name': device_name,
            'known_name': known_name,
            'timestamp': time.time(),
            'advertisement_data': advertisement_data_str
        }


async def main():
    global last_total_number_dev_logs_change_timestamp
    if SCANNER_MODE == 'A':
        scanner = BleakScanner(scanning_mode='active')
    elif SCANNER_MODE == 'P':
        scanner = BleakScanner(scanning_mode='passive')
    else:
        print('main ERROR: unknown SCANNER_MODE = ' + str (SCANNER_MODE))
        return
    scanner.register_detection_callback(simple_callback)
    while True:
        await scanner.start()
        await asyncio.sleep(SCAN_LOOP_DELAY)
        await scanner.stop()
        devices_dict_keys = list(devices_dict.keys())
        for key in devices_dict_keys:
            delay = int(time.time() - devices_dict[key]['timestamp'])
            if delay > FIRST_DEV_LOG_MAX_DELAY:
                del devices_dict[key]
            elif delay > SCAN_LOOP_DELAY:
                devices_dict[key]['RSSI'] = 'N/S'
        devices_dict_keys = list(devices_dict.keys())
        devices_dict_keys.sort(key=devices_dict_sort_by_RSSI_func, reverse=True)
        i = 1
        os.system('cls')
        print('(' + SCANNER_MODE + ') BLE_test v. ' + SCRIPT_VERSION)
        print(common_BLE_aux_lib.get_current_time_str())
        for key in devices_dict_keys:
            print(
                    str(i) + ') -> ' +
                    key + ', ' +
                    common_BLE_aux_lib.get_mac_address_type(key) + ', ' +
                    str(devices_dict[key]['RSSI']) + ', ' +
                    str(devices_dict[key]['device_name']) + ', ' +
                    str(devices_dict[key]['known_name']) + ', ' +
                    str(devices_dict[key]['advertisement_data'])
                )
            i += 1
        if time.time() - last_total_number_dev_logs_change_timestamp > TOTAL_NUMBER_DEV_LOGS_CHANGE_FILE_PERIOD:
            total_number_logs_dict_keys = list(total_number_logs_dict.keys())
            total_number_logs_dict_keys.sort(key=total_number_logs_dict_sort_by_log_count_func, reverse=True)
            i = 1
            f = open(TOTAL_NUMBER_DEV_LOGS_FILE_PATH, 'w')
            f.write('START: ' + script_start_datetime_str + '\n')
            f.write('STOP: ' + common_BLE_aux_lib.get_current_datetime_str() + '\n\n')
            for key in total_number_logs_dict_keys:
                f.write(
                        str(i) + ') -> ' +
                        key + ', ' +
                        common_BLE_aux_lib.get_mac_address_type(key) + ', ' +
                        str(total_number_logs_dict[key]['max_RSSI']) + ', ' +
                        '[' +  str(total_number_logs_dict[key]['first_log_datatime']) + '], ' +
                        '[' +  str(total_number_logs_dict[key]['last_log_datetime']) + '], ' +
                        str(total_number_logs_dict[key]['log_count']) + ', ' +
                        str(total_number_logs_dict[key]['device_name']) + ', ' +
                        str(total_number_logs_dict[key]['known_name']) + ', ' +
                        str(total_number_logs_dict[key]['advertisement_data']) + 
                        '\n'
                    )
                i += 1
            f.close()
            last_total_number_dev_logs_change_timestamp = time.time()


def get_normalized_advertisement_data_str(advertisement_data_str):
    advertisement_data_str = advertisement_data_str.replace('AdvertisementData(', '')
    advertisement_data_str = advertisement_data_str[0:-1]
    return advertisement_data_str


def total_number_logs_dict_sort_by_log_count_func(k):
    return total_number_logs_dict[k]['log_count']


def get_unique_key_idx_in_list(key, keys_list):
    if key not in keys_list:
        return 0
    i = 1
    while key + '_' + str(i) in keys_list:
        i += 1
    if i == MAX_UNIQUE_KEY_IDX and key + '_MAX_UNIQUE_KEY_IDX' in keys_list:
        return MAX_UNIQUE_KEY_IDX + 1
    return i


def devices_dict_sort_by_RSSI_func(k):
    if devices_dict[k]['RSSI'] != 'N/S':
        return devices_dict[k]['RSSI']
    else:
        return -9999
    

#==============================================================================================================================================================================================================================


script_start_datetime_str = common_BLE_aux_lib.get_current_datetime_str()
current_datetime_str_for_filename = common_BLE_aux_lib.get_current_datetime_str_for_filename()
FIRST_DEV_LOG_TIME_FILE_PATH = BASE_PATH + '(' + SCANNER_MODE + ')first_dev_log_time_' + current_datetime_str_for_filename + '.txt'
TOTAL_NUMBER_DEV_LOGS_FILE_PATH = BASE_PATH + '(' + SCANNER_MODE + ')total_number_dev_logs_' + current_datetime_str_for_filename + '.txt'
f = open(FIRST_DEV_LOG_TIME_FILE_PATH, 'a')
f.write('\n\n\n=========================================================================\n')
f.write(common_BLE_aux_lib.get_current_datetime_str() + '\n\n')
f.close()
asyncio.run(main())


