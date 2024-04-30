from serial import Serial

from .bluetooth import connect_socket, get_paired_devices
from .helpers import DeviceInformation, parse_capture
from .led_chksums import led_chksums


class Unicorn():

    def __init__(self, *, dev_port:str = None, dev_mac:str = None, dev_name:str = None, **kwargs) -> None:
        if dev_port:
            self._serial = Serial(dev_port, **kwargs)
        elif dev_mac:
            self._serial = connect_socket(dev_mac)
        else:
            if dev_name:
                for name, mac, port in get_paired_devices(filter_names=False):
                    if name == dev_name:
                        if port:
                            self._serial = Serial(port, **kwargs)
                        else:
                            self._serial = connect_socket(mac)
                        print(f'Connected to {name} ({mac}) {port or ''}')
                        break
                else:
                    raise ValueError(f'Device {dev_name} not found, use opencorn.bluetooth.get_paired_devices(filter_names=False) to show available devices')
            else:
                name, mac, port = get_paired_devices(filter_names=True)[0]
                if port:
                    self._serial = Serial(port, **kwargs)
                else:
                    self._serial = connect_socket(mac)
                print(f'Connected to {name} ({mac}) {port or ''}')


    def close(self):
        self._serial.close()

    def __enter__(self):
        self._serial.__enter__()
        self._serial.write(b'\x65\x3c\x03')
        self._serial.flush()
        dev_info = self._serial.read(45).strip(b'\x00').split(b'\x00')
        self.device_information = DeviceInformation()
        self.device_information.NumberOfEegChannels = int.from_bytes(dev_info[0])
        self.device_information.SerialNum = dev_info[1]
        self.device_information.FwVersion = dev_info[2]
        self.device_information.DeviceVersion = dev_info[3]
        self.device_information.PcbVersion = dev_info[4]
        self.device_information.EnclosureVersion = dev_info[5]
        return self

    def __exit__(self, *args, **kwargs):
        self._serial.__exit__(*args, **kwargs)
    
    def StartAcquisition(self):
        self._serial.write(b'\x61\x7c\x87')
        self._serial.flush()
        self._serial.read(3)
        self.__capture = True

    def GetRawData(self):
        while self.__capture:
            yield self._serial.read(45)
    
    def GetData(self):
        while self.__capture:
            yield parse_capture(self._serial.read(45))

    def StopAcquisition(self):
        self.__capture = False
        self._serial.write(b'\x63\x5c\xc5')
        self._serial.flush()
        self._serial.read(3)

    def GetDigitalOutputs(self):
        self._serial.write(b'\x6b\xdd\xcd')
        self._serial.flush()
        data = self._serial.read(4)[1] # returns 4 bytes: 00 <led_data> <chsum1> <chsum2>
        return data
    
    def SetDigitalOutputs(self, data: int):
        self._serial.write(bytes([0x6a, data, *led_chksums[data]]))
        self._serial.flush()