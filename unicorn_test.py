from opencorn import Unicorn
from time import sleep

# sudo rfcomm bind rfcomm0 60:B6:47:E1:26:06
# https://alberand.com/hc-05-linux.html

# with Unicorn(dev_name='UN-2023.06.03') as device:
# with Unicorn(dev_mac='60:B6:47:E1:26:06') as device:
# with Unicorn(dev_port='/dev/rfcomm0') as device:
with Unicorn() as device:
    device.SetDigitalOutputs(0)
    for i in [0,1,2,3,4,5,6,7,6,5,4,3,2,1,0]:
        device.SetDigitalOutputs(1<<i)
        sleep(.1)
    device.SetDigitalOutputs(0b11111111)
    device.StartAcquisition()
    try:
        print("Start capture")
        for cd in device.GetData():
            # print(f"bat={cd.battery:3.3f}, accX={cd.accX:3.3f}, accY={cd.accY:3.3f}, accZ={cd.accZ:3.3f}", end='\r')
            print(f"bat={cd.battery:3.3f}, gyrX={cd.gyrX:3.3f}, gyrY={cd.gyrY:3.3f}, gyrZ={cd.gyrZ:3.3f}", end='\r')
    except KeyboardInterrupt:
        pass
    device.StopAcquisition()
    device.SetDigitalOutputs(0)
    print("\nEnd capture")

    
