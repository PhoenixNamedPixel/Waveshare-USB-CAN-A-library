MAX_DATA_LENGTH = 8

STANDARD_MASK = 0x7FF
EXTENDED_MASK = 0x1FFFFFFF


class CANFrame:
    """A class representing a CAN frame"""

    def __init__(self, can_id: int, can_data: bytes = b"", is_extended: bool = False, is_rtr: bool = False) -> None:
        """Constructs the data needed for a CAN frame
        Args:
            can_id (int): CAN frame id
            can_data (bytes, optional): CAN frame data. Defaults to empty bytes.
            is_extended (bool, optional): Whether the CAN frame is extended. Defaults to False. **This is unchangable after frame creation.**
            is_rtr (bool, optional): Whether the CAN frame is a remote transmition request. Defaults to False."""
        self._is_extended = is_extended
        self.is_rtr = is_rtr
        self.can_id = can_id
        self.can_data = can_data


    @property
    def can_id(self) -> int:
        return self._can_id

    @can_id.setter
    def can_id(self, can_id: int) -> None:
        self._can_id = can_id & (EXTENDED_MASK if self._is_extended else STANDARD_MASK)

    @property
    def can_data(self) -> bytes:
        return self._can_data

    @can_data.setter
    def can_data(self, can_data: bytes) -> None:
        if len(can_data) > MAX_DATA_LENGTH:
            raise ValueError(f"CAN frame data cannot exceed {MAX_DATA_LENGTH} bytes, provided payload was {len(can_data)} bytes")
        self._can_data = can_data

    @property
    def dlc(self) -> int:
        return len(self._can_data)

    @property
    def is_extended(self) -> bool:
        return self._is_extended

    def __repr__(self) -> str:
        return f"CANFrame(can_id={self.can_id}, can_data={self.can_data}, is_extended={self._is_extended}, is_rtr={self.is_rtr})"