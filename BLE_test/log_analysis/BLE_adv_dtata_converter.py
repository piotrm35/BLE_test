# BLE_adv_dtata_converter
SCRIPT_VERSION = '1.4'


import os
import aux_lib.common_BLE_aux_lib as common_BLE_aux_lib


# Log files must have ".csv" extensions.
BASE_PATH = './'
LOG_FOLDER = BASE_PATH + 'scan_log_1/'


#=================================================================================================================================


# dane z nowego BLE scannera (czarna ikonka - Thingsup)
def NEW_BLE_scanner_adv_data_convert(raw_data):
    print('\n--------------------------------------------------------------------------------')
    print('NEW_BLE_scanner_adv_data_convert')
    print('raw_data = ' + raw_data)
    print('len(raw_data) = ' + str(len(raw_data)))
    print('\n')

    raw_data = raw_data.strip()
    md_data_len_in_bytes = int(raw_data[0:2], 16) - 3
    print('md_data_len_in_bytes = ' + str(md_data_len_in_bytes))
    if md_data_len_in_bytes <= 0:
        return ['manufacturer_data={' + str(raw_data)]
    idx00 = raw_data.index('00')
    print('idx00 = ' + str(idx00))
    try:
        idx000 = raw_data.index('000')
        if idx00 == idx000:
            print('PROBLEM: idx00 == idx000')
    except:
        pass
    if idx00 == 6:
        idx00 = 4
    md_id = int(raw_data[2:idx00], 16)

    int_list = []
    i = idx00 + 2
    while i < 2 * md_data_len_in_bytes + idx00 + 2:
        e = raw_data[i]
        e += raw_data[i + 1]
        i += 2
        int_list.append(int(e, 16))
    md_val_tx = 'manufacturer_data={' + str(md_id) + ': ' + str(bytes(bytearray(int_list))) + '}'
    print(md_val_tx)
    tmp_res = old_BLE_scanner_adv_data_convert(raw_data[i:], False)
    return [md_val_tx] + tmp_res


# dane ze starego BLE scannera (niebieskia ikonka - Bluepixel Technologies)
def old_BLE_scanner_adv_data_convert(raw_data, verbose = True):
    if verbose:
        print('\n--------------------------------------------------------------------------------')
        print('old_BLE_scanner_adv_data_convert')
        print('raw_data = ' + raw_data)
        print('len(raw_data) = ' + str(len(raw_data)))
        print('\n')
    int_list = []
    i = 0
    while i < len(raw_data):
        e = raw_data[i]
        e += raw_data[i + 1]
        i += 2
        int_list.append(int(e, 16))
    res_list = []
    i = 0
    ln_tx = None
    tp_tx = None
    while i < len(int_list):
        if ln_tx is None:
            ln = int_list[i]
            ln_tx = "0x{:02x}".format(ln)
            print('len = ' + ln_tx)
            i += 1
        elif tp_tx is None:
            tp_tx = "0x{:02x}".format(int_list[i])
            tp_key = tp_tx.upper().replace('0X', '')
            if tp_key in list(common_BLE_aux_lib.COMMON_DATA_TYPES_MAP.keys()):
                print('type = ' + tp_tx + '\t ' + common_BLE_aux_lib.COMMON_DATA_TYPES_MAP[tp_key])
            else:
                print('type: ' + tp_tx)
            i += 1
        else:
            tmp_end = i + ln - 1
            tmp_list = []
            while i < tmp_end:
                tmp_list.append(int_list[i])
                i += 1
            if tp_key == 'FF':      # Manufacturer Specific Data
                md_id = tmp_list[1] * 256 + tmp_list[0] 
                val_tx = 'manufacturer_data={' + str(md_id) + ': ' + str(bytes(bytearray(tmp_list[2:]))) + '}'
            elif tp_key == '16':    # Service Data - 16-bit UUID
                service_data_id = "'0000" + "{:02x}".format(tmp_list[1]) + "{:02x}".format(tmp_list[0]) + "-0000-1000-8000-00805f9b34fb'"
                val_tx = 'service_data={' + service_data_id + ': ' + str(bytes(bytearray(tmp_list[2:]))) + '}'
            elif tp_key == '08' or tp_key == '09':    # Shortened Local Name or Complete Local Name
                val_tx = 'local_name=' + str(bytes(bytearray(tmp_list)))
                val_tx = val_tx.replace("=b'", "='")
            else:
                val_tx = str(bytes(bytearray(tmp_list)))
            print(val_tx)
            res_list.append(val_tx)
            ln_tx = None
            tp_tx = None
    return res_list


def line_convert(line_tx):
    data_input_list = line_tx.split(',')
    a = data_input_list[5]
##    res_list = old_BLE_scanner_adv_data_convert(a)
    res_list = NEW_BLE_scanner_adv_data_convert(a)
    advertisement_data_str = ', '.join(res_list)
##    print('advertisement_data_str = ' + advertisement_data_str)
    device_name = str(data_input_list[2])
    if not device_name.strip():
        device_name = '-'
    known_name = '-'
    mac_address = data_input_list[3]
    mac_address_type = common_BLE_aux_lib.get_mac_address_type(mac_address)
    rssi = int(data_input_list[4])
    if mac_address in list(common_BLE_aux_lib.DEV_ADDRESS_MAP.keys()):
        known_name = ':' + common_BLE_aux_lib.DEV_ADDRESS_MAP[mac_address] + ':'
    else:
        known_name = common_BLE_aux_lib.get_known_name_from_advertisement_data_match(advertisement_data_str)
    advertisement_data_str = common_BLE_aux_lib.add_uuid_description_to_advertisement_data_str(advertisement_data_str)
##    result_line = data_input_list[0] + ') ' + data_input_list[1] + ' -> ' + mac_address + ', ' + mac_address_type + ', ' + str(rssi) + ', ' + device_name + ', ' + known_name + ', ' + advertisement_data_str
    result_line = mac_address + ', ' + mac_address_type + ', ' + device_name + ', ' + known_name + ', ' + advertisement_data_str
    return result_line


#=================================================================================================================================


print('SCRIPT START')

log_file_path_list = common_BLE_aux_lib._get_log_path_list(LOG_FOLDER, '.CSV')
for log_file_path in log_file_path_list:
    print('log_file_path: ' + str(log_file_path))
    f = open(log_file_path, mode='r', encoding='utf-8')
    lines_list = f.readlines()
    f.close()
    res_list = []
    i = 0
    for line in lines_list:
        if i > 0:
            res_list.append(line_convert(line))
        i += 1
    
    res_set = set(res_list)
    res_list = []
    i = 0
    for res in res_set:
        res_list.append(str(i + 1) + ') -> ' + res)
        i += 1
    
    f = open(log_file_path.replace('.csv', '.txt'), 'w')
    f.write('\n'.join(res_list))
    f.close()

print('\n')
print('SCRIPT STOP')



