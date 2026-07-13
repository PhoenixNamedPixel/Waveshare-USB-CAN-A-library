from enum import Enum

import serial


class Type(Enum):
    FIXED = 0x02
    VARIABLE = 0x12


class CanSpeed(Enum):
    SPEED_1Mbps = 0x01
    SPEED_800kbps = 0x02
    SPEED_500kbps = 0x03
    SPEED_400kbps = 0x04
    SPEED_250kbps = 0x05
    SPEED_200kbps = 0x06
    SPEED_125kbps = 0x07
    SPEED_100kbps = 0x08
    SPEED_50kbps = 0x09
    SPEED_20kbps = 0x0A
    SPEED_10kbps = 0x0B
    SPEED_5kbps = 0x0C


class CanFrameFormat(Enum):
    STANDARD = 0x01
    EXTENDED = 0x02


class CanMode(Enum):
    NORMAL = 0x00
    SILENT = 0x01
    LOOPBACK = 0x02
    LOOPBACK_SILENT = 0x04


class AutoRetransmit(Enum):
    ENABLED = 0x00
    DISABLED = 0x01


class WaveshareCan:
    """A class to interact with a Waveshare USB CAN A"""

    def __init__(self, port: str, can_speed: CanSpeed = CanSpeed.SPEED_250kbps, baudrate: int = 2000000) -> None:
        """
        Initialize a Waveshare USB CAN A

        Args:
            port: the serial port to connect to
            can_speed: the speed of the can bus, default is 250 kbps
            baudrate: the baudrate of the serial port, default is 2000000
            """
        self.port = port
        self.can_speed = can_speed
        self.baudrate = baudrate
        self.mode = CanMode.NORMAL
        self.send_type = CanFrameFormat.STANDARD
