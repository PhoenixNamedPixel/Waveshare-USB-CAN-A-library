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