from src import *


if __name__ == "__main__":
    adapter = WaveshareCan("COM6")
    adapter.update_configurations(communication_type=Type.FIXED)
    frame = CANFrame(123, b"\x12\x34\x45")
    adapter.send_frame(frame)
    while True:
        received_frame = adapter.read_frame()
        print(received_frame)