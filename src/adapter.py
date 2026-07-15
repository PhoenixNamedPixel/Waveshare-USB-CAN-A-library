from enum import Enum
from CANFrame import CANFrame

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

class WriteException(Exception):
    pass

class ReadException(Exception):
    pass


def calculate_checksum(data: bytes) -> int:
    return sum(data[2:]) & 0xFF


class WaveshareCan:
    """A class to interact with a Waveshare USB CAN A"""

    def __init__(self, port: str, can_speed: CanSpeed = CanSpeed.SPEED_250kbps, baudrate: int = 2000000) -> None:
        """
        Initialize a Waveshare USB CAN A with the serial port already open ready.

        Args:
            port: the serial port to connect to
            can_speed: the speed of the can bus, default is 250 kbps
            baudrate: the baudrate of the serial port, default is 2000000
            """

        # data for serial port
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(self.port, self.baudrate)
        self.open = True

        # data for CAN bus configurations
        self.can_speed = can_speed
        self.type= Type.VARIABLE
        self.send_type = CanFrameFormat.STANDARD
        self.mode = CanMode.NORMAL
        self.auto_retransmit = AutoRetransmit.ENABLED

        self.send_configurations()

        return

    def open_port(self) -> None:
        """Opens the serial port if closed"""
        try:
            if not self.open:
                self.serial.open()
                self.open = True
                print("Port opened")
            else:
                print("Port already open")
        except serial.SerialException as e:
            print('Could not open serial port')
            print(e)
        return

    def close_port(self) -> None:
        """Closes the serial port if open"""
        if self.open:
            self.serial.close()
            self.open = False
            print("Port closed")
        else:
            print("Port not open")
        return

    def _write(self, data: bytes) -> None:
        """Writes the bytes to the serial port"""
        if not self.open:
            raise WriteException('Port not open')

        try:
            sent = self.serial.write(data)
            if sent != len(data):
                raise WriteException('Data not fully sent')
        except serial.SerialException as e:
            raise WriteException(f'Could not send data: {e}')

    def read_frame(self) -> CANFrame:
        """Reads the incoming frame from the serial port
        :return: the incoming frame as a CANFrame object"""
        if not self.open:
            raise ReadException('Port not open')

        try:
            data = self.serial.read(2)
            if (data[0] == 0xaa) and (data[1] & 0xC0 == 0xC0):
                # get frame configurations
                data_length = data[1] & 0xF
                is_rtr = data[1] & 0x10
                is_extended = data[1] & 0x20
                frame_length = data_length + (5 if is_extended else 3) # includes the footer (55)

                # Get the rest of the data
                payload = self.serial.read(frame_length)
                if payload[-1] != 0x55:
                    raise ReadException('Data not received correctly')

                frame_id = int.from_bytes(payload[0:(4 if is_extended else 2)], byteorder='little')
                payload_data = payload[4 if is_extended else 2:-1]

                return CANFrame(frame_id, payload_data, bool(is_extended), bool(is_rtr))

            else:
                raise ReadException('Start of frame received incorrectly')


        except serial.SerialException as e:
            raise ReadException(f'Could not read data: {e}')

    def send_configurations(self) -> None:
        """Sends the configurations to the Waveshare adapter"""
        configurations = bytes([
            0xAA, # Message header
            0x55, # Message footer
            self.type.value, # Fixed vs Variable length
            self.can_speed.value, # Speed of CAN bus
            self.send_type.value, # Standard vs Extended frame
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            self.mode.value,
            self.auto_retransmit.value,
            0x00,
            0x00,
            0x00,
            0x00,
        ])

        configurations += bytes([calculate_checksum(configurations)])
        self._write(configurations)

if __name__ == '__main__':
    device = WaveshareCan('COM6')
    device.open_port()
    device.close_port()
    device.open_port()