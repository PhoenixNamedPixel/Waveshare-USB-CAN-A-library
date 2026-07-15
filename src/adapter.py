from enum import Enum
from typing import Optional

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
            can_speed: the speed of the can bus
            baudrate: the baudrate of the serial port
            """

        # data for serial port
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(self.port, self.baudrate)

        # data for CAN bus configurations
        self.type = Type.VARIABLE
        self.can_speed = can_speed
        self.send_type = CanFrameFormat.STANDARD
        self.mode = CanMode.NORMAL
        self.auto_retransmit = AutoRetransmit.ENABLED

        self.send_configurations()

        return

    def open_port(self) -> None:
        """Opens the serial port if closed"""
        try:
            if not self.serial.is_open:
                self.serial.open()
                print("Port opened")
            else:
                print("Port already open")
        except serial.SerialException as e:
            print('Could not open serial port')
            print(e)
        return

    def close_port(self) -> None:
        """Closes the serial port if open"""
        if self.serial.is_open:
            self.serial.close()
            print("Port closed")
        else:
            print("Port not open")
        return

    def _write(self, data: bytes) -> None:
        """Writes the bytes to the serial port"""
        if not self.serial.is_open:
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
        if not self.serial.is_open:
            raise ReadException('Port not open')

        try:
            """
            This loops until it finds the header byte plus a byte with the first two bits being 1 (C0).
            It will then raise a ReadException if the end byte is not footer (55).
            There can be a rare case where data is aligned so perfectly that there is a AA C0 ... 55 marking a packet when
            there is not one. The library might read this ghost packet accidentally in an extreme edge case and nothing
            can be done to stop this unfortunately
            """
            while True:
                header = self.serial.read(1)[0]
                if header == 0xAA:
                    control = self.serial.read(1)[0]
                    if control & 0xC0 == 0xC0:
                        # get frame configurations
                        data_length = control & 0xF
                        is_rtr = control & 0x10
                        is_extended = control & 0x20
                        frame_length = data_length + (5 if is_extended else 3)  # includes the footer (55)

                        # Get the rest of the data
                        payload = self.serial.read(frame_length)
                        if payload[-1] != 0x55:
                            raise ReadException('Data not received correctly')

                        frame_id = int.from_bytes(payload[0:(4 if is_extended else 2)], byteorder='little')
                        payload_data = payload[4 if is_extended else 2:-1]

                        return CANFrame(frame_id, payload_data, bool(is_extended), bool(is_rtr))

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

    def send_frame(self, frame: CANFrame) -> None:
        """Prepares and sends a frame to the Waveshare adapter
        Args:
            frame: The CANFrame object to be sent to the Waveshare adapter"""
        payload = bytes([
            0xAA,
            0xC0 | (0x20 if frame.is_extended else 0x00) | (0x10 if frame.is_rtr else 0x00) | frame.dlc,
            ])
        payload += frame.can_id.to_bytes(4 if frame.is_extended else 2, byteorder='little')
        payload += frame.can_data
        payload += bytes([0x55])
        self._write(payload)

    def update_configurations(self, communication_type: Optional[Type] = None, can_speed: Optional[CanSpeed] = None, frame_type: Optional[CanFrameFormat] = None, can_mode: Optional[CanMode] = None, auto_retransmit: Optional[AutoRetransmit] = None) -> None:
        """Updates the configurations sent to the Waveshare adapter, add only the settings you want to change, the others will remain the same.
        Args:
            communication_type: The communication type of the configurations sent to the Waveshare adapter, either fixed or variable data length. Use the Type class.
            can_speed: The speed of the can bus. Use the CanSpeed class.
            frame_type: Which type of frame to use, standard to extended. Use the CanFrameFormat class.
            can_mode: The communication mode of the adapter, normal, silent, loopback, and loopback silent. Use the CanMode class.
            auto_retransmit: Automatically retransmit the can frame if failed. Use the AutoRetransmit class."""
        is_changed = False
        if communication_type is not None:
            self.type = communication_type
            is_changed = True
        if can_speed is not None:
            self.can_speed = can_speed
            is_changed = True
        if frame_type is not None:
            self.send_type = frame_type
            is_changed = True
        if can_mode is not None:
            self.mode = can_mode
            is_changed = True
        if auto_retransmit is not None:
            self.auto_retransmit = auto_retransmit
            is_changed = True
        if is_changed:
            self.send_configurations()


if __name__ == '__main__':
    device = WaveshareCan('COM6')
    device.open_port()
    device.close_port()
    device.open_port()