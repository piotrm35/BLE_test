import time
import network
from machine import UART

#------------------------------------------------------------------
# setup:

ESSID_FILTER = 'Gosc'
ROUND_COUNT = 10

#------------------------------------------------------------------

try:
  uart = UART(0, baudrate=19200, bits=8, parity=None, stop=1)
except Exception as e:
  uart = None
  print("WARNING: uart = None")

def my_print(tx):
      try:
        tx = str(tx)
      except:
        tx = "my_print ERROR: str(tx)"
      print(tx)
      if uart is not None:
        uart.write(tx + "\n")
        uart.flush()

#------------------------------------------------------------------

my_print('SCRIP START')

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

for i in range(ROUND_COUNT):
  my_print(str(i+1) + '/' + str(ROUND_COUNT))
  res_list = sta_if.scan()
  for res in res_list:
    if ESSID_FILTER in str(res):
      my_print(str(res))
      time.sleep(1)
      
if uart is not None:
  uart.flush()
  uart.deinit()
my_print('SCRIP STOP')

#------------------------------------------------------------------

