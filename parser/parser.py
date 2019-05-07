import struct
import bitstruct
from parser.packet import DNSRequest, DNSQuestion, DNSResource
from typing import Tuple


class QueryParser:
    @staticmethod
    def parse(packet: bytes) -> DNSRequest:
        (query_id, params, questions_count, answers_count, authority_count,
         additional_count) = struct.unpack_from('>HHHHHH', packet, 0)

        questions = []
        answers = []
        authorities = []
        additionals = []
        position = 13

        for i in range(questions_count):
            question, position = QueryParser.parse_question(packet, position)
            questions.append(question)

        for i in range(answers_count):
            answer, position = QueryParser.parse_resource(packet, position)
            answers.append(answer)

        for i in range(authority_count):
            authority, position = QueryParser.parse_resource(packet, position)
            authorities.append(authority)

        """for i in range(additional_count):
            additional, position = QueryParser.parse_resource(packet, position)
            additionals.append(additional)"""

        return DNSRequest(query_id, params, questions_count, answers_count,
                          authority_count, additional_count, questions)

    @staticmethod
    def parse_name(packet: bytes, from_position: int) -> Tuple[str, int]:
        position = from_position
        name = b''
        while True:
            name_length = struct.unpack_from('>b', packet, position)[0]
            if name_length == 0:
                position += 1
                break
            position += 1

            for j in range(name_length):
                name += struct.unpack_from('c', packet, position)[0]
                position += 1
            name += b'.'
        return name.decode(), position + 1

    @staticmethod
    def parse_question(packet: bytes, from_position: int) -> \
            Tuple[DNSQuestion, int]:

        name, position = QueryParser.parse_name(packet, from_position)
        record_type, cls = struct.unpack_from('>HH', packet, position)
        position += 4

        return DNSQuestion(name, record_type, cls), position

    @staticmethod
    def parse_resource(packet: bytes, from_position: int) -> Tuple[DNSResource,
                                                                   int]:
        _, name_offset = bitstruct.unpack_from('>u2u14', packet, from_position)
        position = from_position + 2
        (record_type, cls, ttl,
         rdlength) = struct.unpack_from('>HHIH', packet, position)
        position += 12
        name, position = QueryParser.parse_name(packet, name_offset)

        position += 12
        data = '.'.join(list(map(str,
                                 struct.unpack_from(
                                     packet,
                                     '>{}'.format('b' * rdlength),
                                     position))))
        position += rdlength

        record = DNSResource(name, record_type, cls, ttl, data)
        return record, position
