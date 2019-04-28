from napalm import get_network_driver

ios_driver = get_network_driver("ios")
ios_device = ios_driver(
    hostname="172.31.83.92",
    username="pyuser",
    password="pypass",
)
ios_device.open()
net_inst = ios_device.get_network_instances()
ios_device.close()
print(net_inst)
