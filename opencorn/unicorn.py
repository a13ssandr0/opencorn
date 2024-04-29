from serial import Serial
from helpers import DeviceInformation
from led_chksums import led_chksums
from helpers import parse_capture


class Unicorn():

    def __init__(self, port_dev, **kwargs) -> None:
        self._port_dev = port_dev
        self._serial = Serial(self._port_dev, **kwargs)

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
        self._serial.write([0x6a, data, *led_chksums[data]])
        self._serial.flush()