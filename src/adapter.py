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


class PortException(Exception):
    pass


class WaveshareCan:
    """A class to interact with a Waveshare USB CAN A"""

    def __init__(self, port: Optional[str], can_speed: CanSpeed = CanSpeed.SPEED_250kbps, baudrate: int = 2000000) -> None:
        """
        Initialize the Waveshare USB CAN A library

        You have the option of either giving a port, and it will be opened immidately, or omit the port so no connection
        will be made

        Args:
            port: the serial port to connect to (If a port is not given, you must use init_port() to initialize it)
            can_speed: the speed of the can bus
            baudrate: the baudrate of the serial port
            """

        # data for CAN bus configurations
        self.type = Type.VARIABLE
        self.can_speed = can_speed
        self.filter_frame_type = CanFrameFormat.STANDARD
        self.mode = CanMode.NORMAL
        self.auto_retransmit = AutoRetransmit.ENABLED

        # data for serial port
        self.baudrate = baudrate
        self.port = None
        self.serial = None
        if port is not None:
            self.init_port(port)

    def init_port(self, port: str) -> None:
        """Initialize and open the serial port if not done on object creation
        Args:
            port: the serial port to connect"""
        self.port = port
        self.serial = serial.Serial(self.port, self.baudrate)
        self.send_configurations()

    def open_port(self) -> None:
        """Opens the serial port if closed"""
        if self.serial is None:
            raise PortException("The port has not been declared")
        try:
            if not self.serial.is_open:
                self.serial.open()
                print("Port opened")
            else:
                print("Port already open")
        except serial.SerialException as e:
            print('Could not open serial port')
            print(e)

    def close_port(self) -> None:
        """Closes the serial port if open"""
        if self.serial is None:
            raise PortException("The port has not been declared")
        if self.serial.is_open:
            self.serial.close()
            print("Port closed")
        else:
            print("Port not open")

    def _write(self, data: bytes) -> None:
        """Writes the bytes to the serial port"""
        if self.serial is None:
            raise PortException("The port has not been declared")
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
        if self.serial is None:
            raise PortException("The port has not been declared")
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
                        frame_length, is_extended, is_rtr = self._parse_control_byte(control)

                        # Get the rest of the data
                        payload = self.serial.read(frame_length)

                        # is_extended and is_rtr are needed to work out the exact frame length for reading the payload
                        return self._parse_frame(payload, is_extended, is_rtr)


        except serial.SerialException as e:
            raise ReadException(f'Could not read data: {e}')

    @staticmethod
    def _parse_control_byte(control) -> tuple[int, bool, bool]:
        """Parses the incoming control byte from the serial port"""
        # get frame configurations
        data_length = control & 0xF
        is_rtr = bool(control & 0x10)
        is_extended = bool(control & 0x20)
        frame_length = data_length + (5 if is_extended else 3)  # includes the footer (55)
        return frame_length, is_extended, is_rtr

    @staticmethod
    def _parse_frame(payload: bytes, is_extended: bool, is_rtr: bool) -> CANFrame:
        """Parses the incoming frame from the serial port into a CANFrame object

        **Note:** this is automatically used within read_frame
        Args:
            payload: The incoming frame from the serial port minus the header and control bits
            is_extended: if the frame is standard or extended
            is_rtr: if the frame is a remote transmission request or not"""
        if payload[-1] != 0x55:
            raise ReadException('Data not received correctly')

        frame_id = int.from_bytes(payload[0:(4 if is_extended else 2)], byteorder='little')
        payload_data = payload[4 if is_extended else 2:-1]

        return CANFrame(frame_id, payload_data, bool(is_extended), is_rtr)

    def send_configurations(self) -> None:
        """Sends the configurations to the Waveshare adapter"""
        configurations = self._prepare_config_payload()
        self._write(configurations)

    def _prepare_config_payload(self) -> bytes:
        """Prepares the configuration payload for the Waveshare adapter
        **Note:** this is automatically used within send_configurations"""
        configurations = bytes([
            0xAA,  # Message header
            0x55,  # Message footer
            self.type.value,  # Fixed vs Variable length
            self.can_speed.value,  # Speed of CAN bus
            self.filter_frame_type.value,  # Standard vs Extended frame
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

        configurations += bytes([self._calculate_checksum(configurations)])
        return configurations

    def send_frame(self, frame: CANFrame) -> None:
        """Prepares and sends a frame to the Waveshare adapter
        Args:
            frame: The CANFrame object to be sent to the Waveshare adapter"""
        payload = self._prepare_frame(frame)
        self._write(payload)

    @staticmethod
    def _prepare_frame(frame: CANFrame) -> bytes:
        """Turns the CAN frame from a CANFrame object to the bytes needed to send to the adapter.

        **Note:** this is automatically used within send_frame
        Args:
            frame: The CAN frame that needs to be turned into bytes
        """
        payload = bytes([
            0xAA,
            0xC0 | (0x20 if frame.is_extended else 0x00) | (0x10 if frame.is_rtr else 0x00) | frame.dlc,
        ])
        payload += frame.can_id.to_bytes(4 if frame.is_extended else 2, byteorder='little')
        payload += frame.can_data
        payload += bytes([0x55])
        return payload

    def update_configurations(self, communication_type: Optional[Type] = None, can_speed: Optional[CanSpeed] = None, filter_frame_type: Optional[CanFrameFormat] = None, can_mode: Optional[CanMode] = None, auto_retransmit: Optional[AutoRetransmit] = None) -> None:
        """Updates the configurations sent to the Waveshare adapter, add only the settings you want to change, the others will remain the same.
        Args:
            communication_type: The communication type of the configurations sent to the Waveshare adapter, either fixed or variable data length. Use the Type class.
            can_speed: The speed of the can bus. Use the CanSpeed class.
            filter_frame_type: Whether to filter for just extended frames or to receive all frames (standard). Use the CanFrameFormat class.
            can_mode: The communication mode of the adapter, normal, silent, loopback, and loopback silent. Use the CanMode class.
            auto_retransmit: Automatically retransmit the can frame if failed. Use the AutoRetransmit class."""
        is_changed = False
        if communication_type is not None:
            self.type = communication_type
            is_changed = True
        if can_speed is not None:
            self.can_speed = can_speed
            is_changed = True
        if filter_frame_type is not None:
            self.filter_frame_type = filter_frame_type
            is_changed = True
        if can_mode is not None:
            self.mode = can_mode
            is_changed = True
        if auto_retransmit is not None:
            self.auto_retransmit = auto_retransmit
            is_changed = True
        if is_changed and self.port is not None:
            self.send_configurations()

    @staticmethod
    def _calculate_checksum(data: bytes) -> int:
        return sum(data[2:]) & 0xFF

if __name__ == '__main__':
    device = WaveshareCan('COM6')
    while True:
        print(device.read_frame())