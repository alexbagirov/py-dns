from typing import List
from itertools import chain
import struct
from parser.header import Header
from parser.query import Query
from parser.answer import Answer
from dnslib import DNSQuestion, DNSRecord, DNSHeader, RR, NS, A


class PacketBuilder:
    @staticmethod
    def build_query(query: Query) -> bytes:
        result = b''
        result += PacketBuilder.build_name(query.name)
        result += struct.pack('>2H', query.record_type, query.record_class)
        return result

    @staticmethod
    def build_answer(answer: Answer) -> bytes:
        result = b''
        result += PacketBuilder.build_name(answer.name)
        result += struct.pack('>2HIH', answer.record_type, answer.record_class,
                              answer.ttl, answer.data_length)
        result += PacketBuilder.build_data(answer.data, answer.record_type)
        return result

    @staticmethod
    def build_data(data: str, record_type: int) -> bytes:
        if record_type == 1:
            result = b''
            for part in data.split('.'):
                result += struct.pack('>B', int(part))
            return result
        else:
            return PacketBuilder.build_name(data)

    @staticmethod
    def build_name(name: str) -> bytes:
        result = b''
        for part in name.strip('.').split('.'):
            result += struct.pack('>B', len(part))
            for letter in part:
                result += struct.pack('>c', letter.encode())
        result += struct.pack('>B', 0)
        return result

    @staticmethod
    def build(header: Header, queries: List[Query], answers: List[Answer],
              authorities: List[Answer], additional: List[Answer]) -> bytes:
        packet = b''
        packet += struct.pack('>6H', header.trans_id, header.flags,
                              len(queries), len(answers),
                              len(authorities), len(additional))

        for query in queries:
            packet += PacketBuilder.build_query(query)

        for answer in chain(answers, authorities, additional):
            packet += PacketBuilder.build_answer(answer)

        packet = DNSRecord(
            DNSHeader(id=header.trans_id, qr=1, aa=1, ra=1))

        for query in queries:
            packet.add_question(DNSQuestion(query.name,
                                            qtype=query.record_type,
                                            qclass=query.record_class))
        for answer in answers:
            packet.add_answer(RR(rname=answer.name,
                                 rtype=answer.record_type,
                                 rclass=answer.record_class,
                                 ttl=answer.ttl,
                                 rdata=A(answer.data)))

        for auth in authorities:
            packet.add_auth(RR(rname=auth.name,
                               rtype=auth.record_type,
                               rclass=auth.record_class,
                               ttl=auth.ttl,
                               rdata=NS(auth.data)))

        for add in additional:
            packet.add_ar(RR(rname=add.name,
                             rtype=add.record_type,
                             rclass=add.record_class,
                             ttl=add.ttl,
                             rdata=A(add.data)))
        return packet.pack()
