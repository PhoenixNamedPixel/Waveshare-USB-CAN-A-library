from src.adapter import WaveshareCan


class TestAdapter:
    """Unit tests for hte underlying logic in adapter.py"""
    def test_control_byte_parsing_valid_lower(self):
        control = 0xC0
        assert WaveshareCan()._parse_control_byte(control) == (3, False, False)

    def test_control_byte_parsing_valid_upper(self):
        control = 0xC8
        assert WaveshareCan()._parse_control_byte(control) == (11, False, False)

    def test_control_byte_parsing_extended_lower(self):
        control = 0xE0
        assert WaveshareCan()._parse_control_byte(control) == (5, True, False)

    def test_control_byte_parsing_extended_upper(self):
        control = 0xE8
        assert WaveshareCan()._parse_control_byte(control) == (13, True, False)