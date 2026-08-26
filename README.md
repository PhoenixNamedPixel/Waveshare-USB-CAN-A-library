# Waveshare USB CAN A adapter library

A lightweight, object-oriented Python library for interacting with the Waveshare USB-CAN-A adapter via a serial interface.

## Features
- Handles both standard (11-bit) and extended (29-bit) CAN IDs
- Supports baud rates from 5 kbps up to 1 Mbps using the CanSpeed enumeration
- Supports Normal, Silent, Loopback, and Loopback-Silent adapter modes.

## Installation
Ensure you have Python installed along with the required serial communication dependency:
```bash
pip install pyserial
```

## Demo
Here is a basic example showing how to initialize the adapter, update its configuration, send a CAN frame, and continuously read incoming frames:
```python
from src import *


if __name__ == "__main__":
    #Initialize the adapter with the correct port
    adapter = WaveshareCan("COM6")

    # Update necessary configurations (fixed is default)
    adapter.update_configurations(communication_type=Type.FIXED)

    # Create a CAN Frame and send it
    frame = CANFrame(123, b"\x12\x34\x45")
    adapter.send_frame(frame)

    # Continuously read incoming frames from the bus
    while True:
        received_frame = adapter.read_frame()
        print(received_frame)
```

## Enum datasheet
An asterisk (*) indicates default
### Type
Controls the communication protocol used over the serial connection, use ```communication_type``` parameter if changing the configuration

| Name     | Meaning                                                                                                                    |
|----------|----------------------------------------------------------------------------------------------------------------------------|
| FIXED*   | Send and receive data with a fixed 20-byte protocol, Highly recommend to use this as it contains a checksum for any errors |
| VARIABLE | Send and receive data with a variable length protocol                                                                      |

### CanSpeed
Tells the Waveshare controller the speed of the CAN bus, use ```can_speed``` parameter if changing the configuration

| Name           |
|----------------|
| SPEED_1Mbps    |
| SPEED_800kbps  |
| SPEED_500kbps  |
| SPEED_400kbps  |
| SPEED_250kbps* |
| SPEED_200kbps  |
| SPEED_125kbps  |
| SPEED_100kbps  |
| SPEED_50kbps   |
| SPEED_20kbps   |
| SPEED_10kbps   |  
| SPEED_5kbps    |

### CanFrameFormat
Sets whether the Waveshare controller only listens for extended frames or both, use ```filter_frame_type``` parameter if changing the configuration

| Name      | Meaning                          |
|-----------|----------------------------------|
| STANDARD* | listens for both frame formats   |
| EXTENDED  | only listens for extended frames |

### CanMode
Sets the communication mode of the Waveshare controller, use ```can_mode``` parameter if changing the configuration

| Name            | Meaning                                                                                                                                        |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| NORMAL*         | Fully active on the physical bus. Transmits frames, acknowledges received frames (ACK bit), sends error frames, and receives external traffic. |
| SILENT          | Can only receive from the bus, cannot transmit (including acknowledgments and errors)                                                          |
| LOOPBACK        | Can only send to the bus, plus receiving its own messages via internal routing, can self acknowledge                                           |
| LOOPBACK_SILENT | Same as loopback except it does not send anything to the bus                                                                                   |

### AutoRetransmit
Automatically retransmit the can frame if failed, use ```auto_retransmit``` parameter if changing the configuration

| Name     |
|----------|
| ENABLED* |
| DISABLED |

## License
Copyright © 2026 Mathew Merry. Distributed under the MIT License. See the LICENSE file for details.