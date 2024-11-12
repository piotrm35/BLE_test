SCRIPT_NAME = "ESP32_BLE_finder"
SCRIPT_VERSION = "1.0"

import time
import bluetooth
from micropython import const
from machine import UART

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


TEXT_TO_FIND_DICT = {'E0:48:24:0D:A9:FA': 'test'}


# ======================================================================================================================================


class BLE_scanner:
    def __init__(self, ble):
      try:
        self.uart = UART(0, baudrate=19200, bits=8, parity=None, stop=1)
      except Exception as e:
        self.uart = None
        self.my_print("__init__ WARNING: self.uart = None")
      self._ble = ble
      self._ble.active(True)
      self._ble.irq(self._irq)
      self.last_print_time = None
      self.my_print("(" + SCANNER_MODE + ") " + SCRIPT_NAME + " v. " + SCRIPT_VERSION)

    def _irq(self, event, data):
      if event == _IRQ_SCAN_RESULT:
        try:
          addr_type, addr, adv_type, rssi, adv_data = data
          tmp_list = self.get_hex_list(addr)
          addr = ":".join(tmp_list)
          addr_type = ADDR_TYPE[str(addr_type)]
          adv_type = ADV_TYPE[str(adv_type)]
          tmp_list = self.get_hex_list(adv_data)
          adv_data = "".join(tmp_list)
          tx = str(time.time()) + ") " + addr_type + " -> " + addr + ", " + str(rssi) + ", " + adv_type + ", " + adv_data
          marker = ''
          for key in TEXT_TO_FIND_DICT.keys():
            if key in tx:
              marker = TEXT_TO_FIND_DICT[key] + ', '
          if marker and (self.last_print_time is None or time.time() - self.last_print_time > 2):
            self.my_print(marker[0:-2] + ' ---> ' + tx)
            self.last_print_time = time.time()
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
      if self.uart is not None:
        self.uart.flush()
        self.uart.deinit()
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
      if self.uart is not None:
        self.uart.write(tx + "\n")
        self.uart.flush()


# --------------------------------------------------------------------------------------------------------------------------------------


def work():
  print("WORK START")
  ble = bluetooth.BLE()
  ble_scanner = BLE_scanner(ble)
  ble_scanner.start_scan()


# ======================================================================================================================================


if __name__ == "__main__":
  work()
  pass

