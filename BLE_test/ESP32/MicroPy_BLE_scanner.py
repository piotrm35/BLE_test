SCRIPT_NAME = "MicroPy_BLE_scanner"
SCRIPT_VERSION = "0.1"

import time
import bluetooth
from micropython import const

_IRQ_SCAN_RESULT = const(5)

# https://docs.micropython.org/en/latest/library/bluetooth.html#class-ble

# 0x00 - PUBLIC
# 0x01 - RANDOM (either static, RPA, or NRPA, the type is encoded in the address itself)
ADDR_TYPE = {"0": "PUBLIC", "1": "RANDOM"}

# 0x00 - ADV_IND - connectable and scannable undirected advertising
# 0x01 - ADV_DIRECT_IND - connectable directed advertising
# 0x02 - ADV_SCAN_IND - scannable undirected advertising
# 0x03 - ADV_NONCONN_IND - non-connectable undirected advertising
# 0x04 - SCAN_RSP - scan response
ADV_TYPE = {
        "0": "ADV_IND",
        "1": "ADV_DIRECT_IND",
        "2": "ADV_SCAN_IND",
        "3": "ADV_NONCONN_IND",
        "4": "SCAN_RSP",
    }

DURATION_MS = 0  # To scan indefinitely, set duration_ms to 0. To stop scanning, set duration_ms to None.
INTERVAL_US = 30000  # default 1280000
WINDOW_US = 20000  # default 11250
SCANNER_MODE = "P"  # P -> passive; A -> active

saved_dev_dict = {}

MAX_DEV_LOG_N = 0  # set MAX_DEV_LOG_N = 0 to log indefinitely


# ======================================================================================================================================


class BLE_scanner:
    def __init__(self, ble, first_dev_log_filename):
        self.first_dev_log_filename = first_dev_log_filename
        self.first_dev_log_file_handler = None
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        self.n = 0
        self.my_print(SCRIPT_NAME + " v. " + SCRIPT_VERSION + " [" + first_dev_log_filename + "]")

        def _irq(self, event, data):
            if event == _IRQ_SCAN_RESULT:
                try:
                    addr_type, addr, adv_type, rssi, adv_data = data
                    addr_type = ADDR_TYPE[str(addr_type)]
                    tmp_list = self.get_hex_list(addr)
                    addr = ":".join(tmp_list)
                    adv_type = ADV_TYPE[str(adv_type)]
                    tmp_list = self.get_hex_list(adv_data)
                    adv_data = "".join(tmp_list)
                    do_log = False
                    if addr not in saved_dev_dict.keys():
                        saved_dev_dict[addr] = [adv_data]
                        do_log = True
                    elif adv_data not in saved_dev_dict[addr]:
                        saved_dev_dict[addr].append(adv_data)
                    do_log = True
                    if do_log:
                        self.my_print(str(time.time()) + ") " + addr_type + " -> " + addr + ", " + str(rssi) + ", " + adv_type + ", " + adv_data)
                        self.n += 1
                    if MAX_DEV_LOG_N > 0 and self.n > MAX_DEV_LOG_N:
                        self.stop_scan()
                except Exception as e:
                    self.my_print("_irq ERROR")
                    self.my_print(e)
                    self.stop_scan()

    def start_scan(self):
        if SCANNER_MODE == "P":
            self._ble.gap_scan(DURATION_MS, INTERVAL_US, WINDOW_US, False)
        elif SCANNER_MODE == "A":
            self._ble.gap_scan(DURATION_MS, INTERVAL_US, WINDOW_US, True)
        else:
            self.my_print("scan ERROR: unknown SCANNER_MODE: " + str(SCANNER_MODE))

    def stop_scan(self):
        self._ble.gap_scan(None)
        print("WORK STOP")

    def get_hex_list(self, raw_data):
        tmp_list = []
        for n in raw_data:
            tmp_list.append("{:02X}".format(n))
        return tmp_list

    def my_print(self, tx):
        try:
            tx = str(tx)
        except:
            tx = "my_print ERROR: str(tx)"
        print(tx)
        if self.first_dev_log_file_handler is None:
            try:
                self.first_dev_log_file_handler = open(self.first_dev_log_filename, "a")
                self.first_dev_log_file_handler.write(tx + "\n")
                self.first_dev_log_file_handler.close()
            except Exception as e:
                self.my_print("my_print ERROR: to file writting")
                self.my_print(e)
            finally:
                self.first_dev_log_file_handler = None
        else:
            print("my_print ERROR: self.first_dev_log_file_handler is not None")


# --------------------------------------------------------------------------------------------------------------------------------------


def work():
    print("WORK START")
    try:
        f = open("BLE_scanner_log_NUMBER.txt", "r")
        tx = f.read()
        f.close()
        NUMBER = int(tx)
    except:
        NUMBER = 0
    first_dev_log_filename = "(SCANNER_MODE)ESP32_first_dev_log_NUMBER.csv.txt"
    first_dev_log_filename = first_dev_log_filename.replace("SCANNER_MODE", SCANNER_MODE)
    first_dev_log_filename = first_dev_log_filename.replace("NUMBER", str(NUMBER))
    print("filename: " + first_dev_log_filename)
    NUMBER += 1
    f = open("BLE_scanner_log_NUMBER.txt", "w")
    f.write(str(NUMBER))
    f.close()
    ble = bluetooth.BLE()
    ble_scanner = BLE_scanner(ble, first_dev_log_filename)
    ble_scanner.start_scan()


# ======================================================================================================================================


if __name__ == "__main__":
    work()


