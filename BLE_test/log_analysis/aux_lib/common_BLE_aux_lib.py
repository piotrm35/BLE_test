# common_BLE_aux_lib
SCRIPT_VERSION = '1.1'


import os
import time, datetime


MAC_PREFIX_00 = '0123'
MAC_PREFIX_01 = '4567'
MAC_PREFIX_10 = '89AB'
MAC_PREFIX_11 = 'CDEF'


try:
    from .UUIDS_DESCRIPTION_MAP import UUIDS_DESCRIPTION_MAP
except:
    print('EXCEPTION: UUIDS_DESCRIPTION_MAP = {}')
    UUIDS_DESCRIPTION_MAP = {}
uuids_description_map_keys = list(UUIDS_DESCRIPTION_MAP.keys())


try:
    from .DEV_MAP import DEV_ADVERTISEMENT_DATA_MAP
except:
    print('EXCEPTION: DEV_ADVERTISEMENT_DATA_MAP = {}')
    DEV_ADVERTISEMENT_DATA_MAP = {}
dev_advertisement_data_map_keys = list(DEV_ADVERTISEMENT_DATA_MAP.keys())


match_ind_dict = {}


#==============================================================================================================================================================================================================================
# Public:


try:
    from .DEV_MAP import DEV_ADDRESS_MAP
except:
    print('EXCEPTION: DEV_ADDRESS_MAP = {}')
    DEV_ADDRESS_MAP = {}


try:
    from .COMMON_DATA_TYPES_MAP import COMMON_DATA_TYPES_MAP
except:
    print('EXCEPTION: COMMON_DATA_TYPES_MAP = {}')
    COMMON_DATA_TYPES_MAP = {}


def get_known_name_from_advertisement_data_match(advertisement_data_str):
    if len(dev_advertisement_data_map_keys) > 0:
        global match_ind_dict
        match_ind_dict = {}
        advertisement_data_dict = get_advertisement_data_dict(advertisement_data_str)
        advertisement_data_dict_keys = list(advertisement_data_dict.keys())
        for dev_advertisement_data_map_key in dev_advertisement_data_map_keys:
            dev_advertisement_data_map_key_dict = get_advertisement_data_dict(dev_advertisement_data_map_key)                
            dev_advertisement_data_map_key_dict_keys = list(dev_advertisement_data_map_key_dict.keys())
            match_ind = ''
            if len(dev_advertisement_data_map_key_dict_keys) > 0:
                for key in advertisement_data_dict_keys:
                    if is_key_prefix_in_keys_list(key, dev_advertisement_data_map_key_dict_keys):
                        if is_equality_in_key_and_key_prefix_dicts(key, advertisement_data_dict, dev_advertisement_data_map_key_dict):
                            if len(match_ind) > 0:
                                match_ind += ','
                            match_ind += get_name_shortcut(key)
                        else:
                            match_ind = ''
                            break
            match_ind_dict[dev_advertisement_data_map_key] = match_ind
        match_ind_dict_keys = list(match_ind_dict.keys())
        match_ind_dict_keys.sort(key=match_ind_dict_sort_by_list_len_func, reverse=True)
        if len(match_ind_dict[match_ind_dict_keys[0]]) > 0:
            return DEV_ADVERTISEMENT_DATA_MAP[match_ind_dict_keys[0]] + '(' + match_ind_dict[match_ind_dict_keys[0]] + ')'
    return '-'


def add_uuid_description_to_advertisement_data_str(advertisement_data_str): # service_data={00003802-0000-1000-8000-00805f9b34fb: _bc._f6_bc_c6_a3} service_uuids=[00001011-0000-1000-8000-00805f9b34fb, 00001012-0000-1000-8000-00805f9b34fb, 0000e011-0000-1000-8000-00805f9b34fb]
    if 'service_uuids=[' in advertisement_data_str:
        tmp_list = advertisement_data_str.split('service_uuids=[')
        tmp_data = tmp_list[1].split(']')[0]
        desc = ''
        for uuid in uuids_description_map_keys:
            if uuid in tmp_data:
                if len(desc) > 0:
                    desc += ', '
                desc += UUIDS_DESCRIPTION_MAP[uuid]
        if len(desc) > 0:
            advertisement_data_str = advertisement_data_str.replace('service_uuids=[' + tmp_data + ']', 'service_uuids=[' + tmp_data + ']=>[' + desc + ']')
    if 'service_data={' in advertisement_data_str:
        tmp_list = advertisement_data_str.split('service_data={')
        tmp_data = tmp_list[1].split('}')[0]
        desc = ''
        for uuid in uuids_description_map_keys:
            if uuid in tmp_data:
                if len(desc) > 0:
                    desc += ', '
                desc += UUIDS_DESCRIPTION_MAP[uuid]
        if len(desc) > 0:
            advertisement_data_str = advertisement_data_str.replace('service_data={' + tmp_data + '}', 'service_data={' + tmp_data + '}=>[' + desc + ']')
    return advertisement_data_str


def get_advertisement_data_dict(advertisement_data_str):
    advertisement_data_dict = {}
    for advertisement_data_str_item in advertisement_data_str.split(', '):
        advertisement_data_str_item_list = advertisement_data_str_item.split('=')
        if len(advertisement_data_str_item_list) == 2:
            advertisement_data_dict[advertisement_data_str_item_list[0]] = advertisement_data_str_item_list[1]
    return advertisement_data_dict


def get_mac_address_type(mac_str):
    a = mac_str[0:1]
    if a in MAC_PREFIX_00:
        return 'NrPA'   # Non-resolvable Private Address
    elif a in MAC_PREFIX_01:
        return 'RPA'    # Resolvable Private Address
    elif a in MAC_PREFIX_10:
        return 'RES'    # Reserved for future use
    elif a in MAC_PREFIX_11:
        return 'SDA'    # Static Device Address
    else:
        return 'ERROR'


def get_current_time_str():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')


def get_current_datetime_str():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y-%H:%M:%S')


def get_current_datetime_str_for_filename():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y-%H_%M_%S')


# this function gets log files paths from subfolders as well
def _get_log_path_list(root_folder, extension):
    res_list = []
    for (dir_path, dir_names, file_names) in os.walk(root_folder):
        res_list += [os.path.join(dir_path, f) for f in file_names if os.path.splitext(f)[1].upper() == extension]
##    print('get_log_path_list: res_list = ' + str(res_list))
    return res_list


def get_mac_address_set(field_set):
    res_list = []
    for field in field_set:
        if ' -> ' in field:
            tx_list = field.split(' -> ')
            if len(tx_list) > 1:
                res_list.append(tx_list[1].strip())
##    print('get_mac_address_set: res_list = ' + str(res_list))
    return set(res_list)


def get_manufacturer_data_set(field_set):
    res_list = []
    for field in field_set:
        if field.startswith('manufacturer_data'):
            res_list.append(field)
##    print('get_manufacturer_data_set: res_list = ' + str(res_list))
    return set(res_list)


def get_service_uuids_set(field_set):
    res_list = []
    for field in field_set:
        if field.startswith('service_uuids'):
            res_list.append(field)
##    print('get_service_uuids_set: res_list = ' + str(res_list))
    return set(res_list)


def get_service_data_set(field_set):
    res_list = []
    for field in field_set:
        if field.startswith('service_data'):
            res_list.append(field)
##    print('get_service_data_set: res_list = ' + str(res_list))
    return set(res_list)


def get_local_name_set(field_set):
    res_list = []
    for field in field_set:
        if field.startswith('local_name'):
            res_list.append(field)
##    print('get_local_name_set: res_list = ' + str(res_list))
    return set(res_list)


#-------------------------------------------------------------------------------------------------------------------------
# Private:


def get_name_shortcut(name):
    res = ''
    name_list = name.split('_')
    for k in name_list:
        res += k[0]
    return res


def is_equality_in_key_and_key_prefix_dicts(key, key_dict, key_prefix_dict):
    key_prefix_dict_keys = list(key_prefix_dict.keys())
    for key_prefix_dict_key in key_prefix_dict_keys:
        if key_prefix_dict_key.startswith(key):
            if key_dict[key] == key_prefix_dict[key_prefix_dict_key]:
                return True
    return False


def is_key_prefix_in_keys_list(key_prefix, keys_list):
    for key in keys_list:
        if key.startswith(key_prefix):
            return True
    return False


def match_ind_dict_sort_by_list_len_func(k):
    tmp = match_ind_dict[k].split(',')
    i = 0
    for el in tmp:
        if len(el) > 0:
            i += 1
    return i


#==============================================================================================================================================================================================================================


if __name__ == '__main__':
    pass



