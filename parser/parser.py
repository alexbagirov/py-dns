import struct
from parser.query import Query
from parser.reader import PacketReader


class QueryParser:
    @staticmethod
    def parse(packet: bytes) -> Query:
        reader = PacketReader(packet)
        query_id = struct.unpack('>H', reader.read(2))
        params = struct.unpack('>H', reader.read(2))
        questions_count = struct.unpack('>H', reader.read(2))
        answers_count = struct.unpack('>H', reader.read(2))
        authority_count = struct.unpack('>H', reader.read(2))
        additional_count = struct.unpack('>H', reader.read(2))

        return Query()
