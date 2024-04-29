#sudo apt install python3-serial python3-gi python3-gi-cairo gir1.2-gtk-4.0


from gi.repository import Gio
from socket import socket, AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM


mngr_proxy = Gio.DBusProxy.new_for_bus_sync(
            bus_type=Gio.BusType.SYSTEM,
            flags=Gio.DBusProxyFlags.NONE,
            info=None,
            name='org.bluez', #bus_name
            object_path='/',
            interface_name='org.freedesktop.DBus.ObjectManager',
            cancellable=None)


def getPairedDevices(filter_names: bool = True):
    devs = []
    for obj_path, obj_data in mngr_proxy.GetManagedObjects().items():
        device_data = obj_data.get('org.bluez.Device1', {})
        uuids = device_data.get('UUIDs', [])
        name = device_data.get('Alias') or device_data.get('Name') or ''
        if '00001101-0000-1000-8000-00805f9b34fb' in uuids and (not filter_names or name.startswith('UN-')):
            #print(f'Device [{name}] on object path: {obj_path}')
            devs.append((name, device_data.get('Address')))
    return devs



def findRFCOMMport(dev_addr: str):
    # Establish connection and setup serial communication
    for i in range(1,31):
        try:
            s = socket(AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM)
            s.connect((dev_addr, i))
            return s
        except OSError:
            print(f"Invalid port number: {i}")
    else:
        raise ConnectionError(f"Device {dev_addr} is not listening on any RFCOMM channel (1-30)")