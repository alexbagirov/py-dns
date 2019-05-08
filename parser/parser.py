import struct
from typing import Tuple, NoReturn

from parser.answer import Answer
from parser.header import Header
from parser.query import Query


class PackerParser:
    @staticmethod
    def parse_response(packet: bytes) -> NoReturn:
        header = PackerParser.parse_resp_headers(packet)
        print(header)
        offset = 12

        queries = []
        for i in range(header.queries_count):
            query, offset = PackerParser.parse_query(packet, offset)
            queries.append(query)
        print(queries)

        answers = []
        for i in range(header.answers_count):
            answer, offset = PackerParser.parse_answer(packet, offset)
            answers.append(answer)
        print(answers)

    @staticmethod
    def parse_resp_headers(packet: bytes) -> Header:
        trans_id = struct.unpack_from('>H', packet, offset=0)[0]
        flags = struct.unpack_from('>H', packet, offset=2)[0]
        questions_count = struct.unpack_from('>H', packet, offset=4)[0]
        answers_count = struct.unpack_from('>H', packet, offset=6)[0]
        auth_count = struct.unpack_from('>H', packet, offset=8)[0]
        additional_count = struct.unpack_from('>H', packet, offset=10)[0]
        return Header(trans_id, flags, questions_count,
                      answers_count, auth_count, additional_count)

    @staticmethod
    def parse_query(packet: bytes, offset: int) -> Tuple[Query, int]:
        name, offset = PackerParser.parse_name(packet, offset)
        record_type = struct.unpack_from('>H', packet, offset=offset)[0]
        record_class = struct.unpack_from('>H', packet, offset=offset+2)[0]
        return Query(name, record_type, record_class), offset + 4

    @staticmethod
    def parse_name(packet: bytes, offset: int) -> Tuple[str, int]:
        name = b''
        position = offset
        label_length = struct.unpack_from('>B', packet, position)[0]
        position += 1
        while label_length:
            name += b''.join(struct.unpack_from(f'>{"c" * label_length}',
                                                packet, position))
            name += b'.'
            position += label_length
            label_length = struct.unpack_from('>B', packet, position)[0]
            position += 1
        return name.decode(), position

    @staticmethod
    def parse_answer(packet: bytes, offset: int) -> Tuple[Answer, int]:
        name_offset = struct.unpack_from('>H', packet, offset=offset)[0] & 16383
        name, _ = PackerParser.parse_name(packet, name_offset)

        record_type = struct.unpack_from('>H', packet, offset=offset + 2)[0]
        record_class = struct.unpack_from('>H', packet, offset=offset + 4)[0]
        ttl = struct.unpack_from('>H', packet, offset=offset + 6)[0]
        data_length = struct.unpack_from('>H', packet, offset=offset + 10)[0]

        data = '.'.join(
            map(str, [struct.unpack_from(f'>B', packet, offset=offset + 12 + i)[0]
                for i in range(data_length)]))

        return Answer(name, record_type, record_class, ttl, data_length,
                      data), offset + 12 + data_length
