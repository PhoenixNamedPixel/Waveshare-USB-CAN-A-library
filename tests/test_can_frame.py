import pytest
from src.CANFrame import CANFrame


class TestCanFrame:
    def test_default_init(self):
        frame = CANFrame(123)
        assert frame.can_id == 123
        assert frame.can_data == b""
        assert not frame.is_extended
        assert not frame.is_rtr
        assert frame.dlc == 0


    def test_default_init_with_rtr(self):
        frame = CANFrame(123, is_rtr=True)
        assert frame.can_id == 123
        assert frame.can_data == b""
        assert not frame.is_extended
        assert frame.is_rtr
        assert frame.dlc == 0


    def test_default_init_with_extended(self):
        frame = CANFrame(123, is_extended=True)
        assert frame.can_id == 123
        assert frame.can_data == b""
        assert frame.is_extended
        assert not frame.is_rtr
        assert frame.dlc == 0

    def test_default_init_with_both(self):
        frame = CANFrame(123, is_extended=True, is_rtr=True)
        assert frame.can_id == 123
        assert frame.can_data == b""
        assert frame.is_extended
        assert frame.is_rtr
        assert frame.dlc == 0


    def test_large_number_when_standard(self):
        with pytest.raises(ValueError):
            CANFrame(2048)

    def test_large_number_when_extended(self):
        frame = CANFrame(2049, is_extended=True)
        assert frame.can_id == 2049

    def test_excessive_number_when_extended(self):
        with pytest.raises(ValueError):
            CANFrame(536870912, is_extended=True)

    def test_providing_data(self):
        data = b"\x12\x34\x56"
        frame = CANFrame(123, can_data=data)
        assert frame.can_data == data
        assert frame.dlc == 3

    def test_too_much_data(self):
        with pytest.raises(ValueError):
            data = b"\x12\x34\x56\x78\x90\xab\xcd\xef\x12" # 9 length
            CANFrame(123, can_data=data)

    def test_repr(self):
        data = b"\x12\x34\x56"
        frame = CANFrame(123, can_data=data)
        assert repr(frame) == "CANFrame(can_id=123, can_data=123456, is_extended=False, is_rtr=False)"

    def test_min_id(self):
        frame = CANFrame(0)
        assert frame.can_id == 0

    def test_neg_id(self):
        with pytest.raises(ValueError):
            CANFrame(-1)

    def test_max_standard_id(self):
        frame = CANFrame(2047)
        assert frame.can_id == 2047

    def test_max_extended_id(self):
        frame = CANFrame(536870911, is_extended=True)
        assert frame.can_id == 536870911

    def test_max_data(self):
        data = b"\x12\x34\x56\x78\x90\xab\xcd\xef" # 8 length
        frame = CANFrame(123, can_data=data)
        assert frame.can_data == data
        assert frame.dlc == 8

    def test_modify_extended_error(self):
        with pytest.raises(AttributeError):
            frame = CANFrame(123, is_extended=True)
            # noinspection PyPropertyAccess
            frame.is_extended = False
        assert frame.is_extended