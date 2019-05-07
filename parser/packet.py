from typing import List


class DNSQuestion:
    def __init__(self, name: str, record_type: int, cls: int):
        self.name = name
        self.record_type = record_type
        self.cls = cls


class DNSResource:
    def __init__(self, name: str, record_type: int, cls: int, ttl: int,
                 record_data: str):
        self.name = name
        self.record_type = record_type
        self.cls = cls
        self.ttl = ttl
        self.record_data = record_data


class DNSRequest:
    def __init__(self, query_id: int, params: int, questions_count: int,
                 answers_count: int, authority_count: int,
                 additional_count: int, questions: List[DNSQuestion],
                 answers: List[DNSResource] = None,
                 authoritative: List[DNSResource] = None,
                 additional: List[DNSResource] = None):
        self.query_id = query_id
        self.params = params
        self.questions_count = questions_count
        self.answers_count = answers_count
        self.authority_count = authority_count
        self.additional_count = additional_count
        self.questions = questions
        self.answers = answers
        self.authoritative = authoritative
        self.additional = additional
