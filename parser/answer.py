class Answer:
    def __init__(
        self,
        name: str,
        record_type: int,
        record_class: int,
        ttl: int,
        data_length: int,
        data: str,
    ):
        self.name = name
        self.record_type = record_type
        self.record_class = record_class
        self.ttl = ttl
        self.data_length = data_length
        self.data = data

    def __str__(self):
        return (
            f"{self.name}, Type: {self.record_type}, "
            f"Class: {self.record_class}, TTL: {self.ttl}, "
            f"Data: {self.data}"
        )

    def __repr__(self):
        return self.__str__()
