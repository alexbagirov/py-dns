import struct
from typing import Tuple, List, Optional

from parser.record import Record
from parser.header import Header
from parser.query import Query


class PackerParser:
    @staticmethod
    def parse_response(packet: bytes) -> Tuple[List[Query], List[Record],
                                               List[Record], List[Record]]:
        header = PackerParser.parse_resp_headers(packet)
        offset = 12

        queries = []
        for i in range(header.queries_count):
            query, offset = PackerParser.parse_query(packet, offset)
            queries.append(query)

        answers = []
        for i in range(header.answers_count):
            answer, offset = PackerParser.parse_record(packet, offset)
            answers.append(answer)

        authorities = []
        for i in range(header.auth_count):
            auth, offset = PackerParser.parse_record(packet, offset)
            authorities.append(auth)

        additional = []
        for i in range(header.additional_count):
            result = PackerParser.parse_record(packet, offset)
            if not result:
                break
            add, offset = result
            additional.append(add)

        return queries, answers, authorities, additional

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
        if label_length == 192:
            suffix_offset = struct.unpack_from('>H', packet, offset=position)[0] & 16383
            return PackerParser.parse_name(packet, suffix_offset)[0], position
        position += 1
        while label_length:
            name += b''.join(struct.unpack_from(f'>{"c" * label_length}',
                                                packet, position))
            name += b'.'
            position += label_length
            label_length = struct.unpack_from('>B', packet, position)[0]
            if label_length == 192:
                suffix_offset = struct.unpack_from('>H', packet, offset=position)[0] & 16383
                position += 2
                return name.decode() + PackerParser.parse_name(packet, suffix_offset)[0], position
            position += 1
        return name.decode(), position

    @staticmethod
    def parse_record(packet: bytes, offset: int) -> Optional[Tuple[Record, int]]:
        name_offset = struct.unpack_from('>H', packet, offset=offset)[0] & 16383
        if name_offset == 0:
            return None
        name, _ = PackerParser.parse_name(packet, name_offset)

        record_type = struct.unpack_from('>H', packet, offset=offset + 2)[0]
        if record_type not in (1, 2):
            return None
        record_class = struct.unpack_from('>H', packet, offset=offset + 4)[0]
        ttl = struct.unpack_from('>I', packet, offset=offset + 6)[0]
        data_length = struct.unpack_from('>H', packet, offset=offset + 10)[0]

        if record_type == 1:
            data = '.'.join(
                map(str, [struct.unpack_from(f'>B', packet, offset=offset + 12 + i)[0]
                    for i in range(data_length)]))
        else:
            data = PackerParser.parse_name(packet, offset + 12)[0]

        return Record(name, record_type, record_class, ttl, data_length,
                      data), offset + 12 + data_length
