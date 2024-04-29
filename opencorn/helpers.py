__all__ = [
    "CaptureData",
    "ChannelIndex",
    "DeviceInformation",
    "GetChannelIndex",
    "parse_capture",
]


from typing import NamedTuple
from enum import IntEnum


class DeviceInformation():
    NumberOfEegChannels: int
    SerialNum: str
    FwVersion: str
    DeviceVersion: str
    PcbVersion: str
    EnclosureVersion: str


def GetChannelIndex(name:str):
    return ChannelIndex[name.replace(' ', '_')].value


class ChannelIndex(IntEnum):
    EEG_1 = 0
    EEG_2 = 1
    EEG_3 = 2
    EEG_4 = 3
    EEG_5 = 4
    EEG_6 = 5
    EEG_7 = 6
    EEG_8 = 7
    Accelerometer_X = 8
    Accelerometer_Y = 9
    Accelerometer_Z = 10
    Gyroscope_X = 11
    Gyroscope_Y = 12
    Gyroscope_Z = 13
    Counter = 14
    Battery_Level = 15
    Validation_Indicator = 16


class CaptureData(NamedTuple):
    battery: int
    '''Battery level in percent'''

    eeg1: int
    '''EEG channel 1 in microvolts'''
    eeg2: int
    '''EEG channel 2 in microvolts'''
    eeg3: int
    '''EEG channel 3 in microvolts'''
    eeg4: int
    '''EEG channel 4 in microvolts'''
    eeg5: int
    '''EEG channel 5 in microvolts'''
    eeg6: int
    '''EEG channel 6 in microvolts'''
    eeg7: int
    '''EEG channel 7 in microvolts'''
    eeg8: int
    '''EEG channel 8 in microvolts'''

    accX: int
    '''Accelerometer X in g'''
    accY: int
    '''Accelerometer Y in g'''
    accZ: int
    '''Accelerometer Z in g'''

    gyrX: int
    '''Gyroscope X in deg/s'''
    gyrY: int
    '''Gyroscope Y in deg/s'''
    gyrZ: int
    '''Gyroscope Z in deg/s'''
    
    counter: int
    '''Sample counter'''


# https://github.com/unicorn-bi/Unicorn-Suite-Hybrid-Black/blob/master/Unicorn%20Bluetooth%20Protocol/UnicornBluetoothProtocol.pdf
def parse_capture(payload: bytes):
    payload = list(payload)

    # get battery level in percent
    data = [100 * (payload[2] & 0xF) / 15]

    # get eeg in microvolts
    for i in range(3,25,3):
        eeg = payload[i] << 16 | payload[i+1] << 8 | payload[i+2]
        # check if first bit is 1 (2s complement)
        if eeg &   0x00800000:
            eeg |= 0xFF000000
        # convert to eeg value in microvolts
        data.append(eeg * 4500000/50331642)

    # get accelerometer x,y,z in g
    for i in range(27, 32, 2):
        acc = (payload[i] | payload[i+1]<<8)
        if acc &   0x008000:
            acc -= 1<<16
        data.append(acc / 4096)

    # get gyroscope x,y,z in deg/s
    for i in range(33, 38, 2):
        gyr = (payload[i] | payload[i+1]<<8)
        if gyr &   0x008000:
            gyr -= 1<<16
        data.append(gyr / 32.8)

    # get counter
    data.append(payload[39] | payload[40] << 8 | payload[41] << 16 | payload[42] << 24)

    return CaptureData(*data)


if __name__ == '__main__':
    print('Payload parser test')
    payload = [0xC0, 0x00, 0x0F, 0x00, 0x9F, 0xAF, 0x00, 0x9F, 0xD4, 0x00, 0xA0,
               0x40, 0x00, 0x9F, 0x43, 0x00, 0x9F, 0x9A, 0x00, 0x9F, 0xE3, 0x00,
               0x9F, 0x85, 0x00, 0x9F, 0xBB, 0x2E, 0xF6, 0xE9, 0x02, 0x8D, 0xF2,
               0xF3, 0xFF, 0xEF, 0xFF, 0x23, 0x00, 0xB0, 0x00, 0x00, 0x00, 0x0D, 0x0A]
    
    from pprint import pprint
    cd = parse_capture(payload)
    cd.gyrX
    pprint(cd._asdict())