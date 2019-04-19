from io import BytesIO


class PacketReader:
    def __init__(self, packet: bytes):
        self.packet = BytesIO(packet)

    def read(self, size: int) -> bytes:
        return self.packet.read(size)
