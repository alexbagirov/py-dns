class Query:
    def __init__(self, name: str, record_type: int, record_class: int):
        self.name = name
        self.record_type = record_type
        self.record_class = record_class

    def __str__(self):
        return f"{self.name}, Type: {self.record_type}, " f"Class: {self.record_class}"

    def __repr__(self):
        return self.__str__()
