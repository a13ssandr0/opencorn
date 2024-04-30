# Opencorn

Open-source Python library for [g.tec Unicorn Hybrid Black](https://www.gtec.at/product/unicorn-hybrid-black/).

![](https://www.gtec.at/wp-content/uploads/2023/09/unicorn-hybrid-black-bundle.jpg)

## Installing
### Requirements
#### Linux
```sh
sudo apt install python3-serial python3-gi python3-gi-cairo gir1.2-gtk-4.0
```
#### Windows
- Python (with pip)
- `pip install pywin32`

## Usage

### Import

```python
from opencorn import Unicorn
```

### Connection and data acquisition

The headset must be already paired at this stage, the library will NOT handle discovery and pairing, use the interface/methods provided by your operating system.

The code below finds the headset from the paired devices and automatically connects to it, starts the capture and displays data from the battery and the gyroscope until the user terminates the program with CTRL+C.

```python
from opencorn import Unicorn

with Unicorn() as device:
    device.StartAcquisition()
    try:
        print("Start capture")
        for cd in device.GetData():
            print(f"bat={cd.battery:3.3f}, gyrX={cd.gyrX:3.3f}, gyrY={cd.gyrY:3.3f}, gyrZ={cd.gyrZ:3.3f}", end='\r')
    except KeyboardInterrupt:
        pass
    device.StopAcquisition()
    print("\nEnd capture")

```

`GetData()` is a [generator](https://wiki.python.org/moin/Generators) yielding a `CaptureData` object that contains the parsed data received from the headset. To get the raw data you can use `GetRawData()` instead.

### Controlling the LEDs

The right bow of the headset has 8 programmable LEDs.

To set the state of the LEDs you have to set the bits of an 8-bit integer (0-255),
so 0 means all the LEDs off and 255 all the LEDs on

| Right to left | LED 7 | LED 6 | LED 5 | LED 4 | LED 3 | LED 2 | LED 1 | LED 0 |
| ------------- | ----- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| 0bABCDEFGH    | A     | B     | C     | D     | E     | F     | G     | H     |

```python
from opencorn import Unicorn

with Unicorn() as device:
    # turn all the LEDs off
    device.SetDigitalOutputs(0)

    # run a chaser effect with LEDs turning on and off
    # one after the other back and forth
    for i in [0,1,2,3,4,5,6,7,6,5,4,3,2,1,0]:
        device.SetDigitalOutputs(1<<i)
        sleep(.1)
  
    # turn all the LEDs on
    #device.SetDigitalOutputs(0b1111111)
    device.SetDigitalOutputs(255)
    sleep(4)
    device.SetDigitalOutputs(0)
```

`GetDigitalOutputs()` returns an integer (like above) representing the state of the LEDs

## Connecting to a specific device

The constructor `Unicorn()` supports arguments to select to which device should connect:

|                                      |                                                                     |
| ------------------------------------ | ------------------------------------------------------------------- |
| Unicorn()                            | Automatically selects the first Unicorn device available            |
| Unicorn(dev_port='/dev/rfcomm0')     | Connect to the provided serial port                                 |
| Unicorn(dev_mac='AA:BB:CC:DD:EE:FF') | Connect (with a socket) to the device with the provided mac address |
| Unicorn(dev_name='UN-2023.06.03')    | Connect to the device with the provided name                        |

### Getting the list of the available devices
`Unicorn()` and `Unicorn(dev_name='...')` internally call the method `get_paired_devices(filter_names: bool = True)` that handles the system api calls to get the list of serial devices already paired.

The parameter `filter_names` (enabled for `Unicorn()` and disabled `Unicorn(dev_name='...')`) enables the filter to only get those devices which name starts with "UN-".

If you need to get the list of the devices you can import the method from the internal bluetooth library
```python
from opencorn.bluetooth import get_paired_devices

...
devices = get_paired_devices(filter_names=False)
...

```