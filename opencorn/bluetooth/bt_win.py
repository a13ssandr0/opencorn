import os
if os.name != 'nt':
    raise ImportError(f"Windows module cannot be imported on your system ({os.name})")

from re import compile
import serial.tools.list_ports as list_ports
import win32com.client as win32


## 'BTHENUM\\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0002\\7&4ABA4C4&0&AABBCCDDEEFF_C00000000'
hwid_rex = compile(r'BTHENUM\\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&[\dA-F]{4}\\[\dA-F]&[\dA-F]{7}&[\dA-F]&([\dA-F]{12})_[\dA-F]+')

wmi_service = win32.GetObject("winmgmts:\\\\.\\root\\cimv2")


def get_paired_devices(filter_names: bool = True) -> list[tuple[str, str, str]]:
    serial_devs = []

    for port in list_ports.comports():
        m = hwid_rex.match(port.hwid)
        if m and m[1] != '000000000000':
            serial_devs.append(('', m[1], port.device))

    serial_bt_devs = []

    for dev in wmi_service.ExecQuery(r'SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE "%BLUETOOTHDEVICE%"'):
        name:str = dev.Caption or dev.Name or ''

        if filter_names and not name.startswith('UN-'):
            continue

        for _, hwid, com_dev in serial_devs:
            if dev.HardwareID[0][-12:] == hwid:
                ## HardwareID: ('BTHENUM\\Dev_AABBCCDDEEFF',)
                #serial_bt_devs.append((name, dev.HardwareID[0].split('_')[1], com_dev))
                serial_bt_devs.append((name, hwid, com_dev))

    return serial_bt_devs
