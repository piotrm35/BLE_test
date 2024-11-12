import network
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()
# sta_if.connect('2tel', 'password')
# sta_if.isconnected()
# sta_if.ifconfig()

# import mip
# mip.install('aioble')
# mip.install('ble_advertising')


