import os
from socket import socket, AF_BLUETOOTH, SOCK_STREAM, BTPROTO_RFCOMM

if os.name == 'nt':
    from bt_win import get_paired_devices
elif os.name == 'posix':
    from bt_linux import get_paired_devices
else:
    def get_paired_devices(_=True) -> list[tuple[str, str, str]]:
        raise NotImplementedError(f'Device discovery is not supported on your system ({os.name})')


def connect_socket(dev_addr: str):
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