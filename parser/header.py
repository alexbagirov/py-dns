class Header:
    def __init__(
        self,
        trans_id: int,
        flags: int,
        questions_count: int,
        answers_count: int,
        auth_count: int,
        additional_count: int,
    ):
        self.trans_id = trans_id
        self.flags = flags
        self.queries_count = questions_count
        self.answers_count = answers_count
        self.auth_count = auth_count
        self.additional_count = additional_count

    def __str__(self):
        return (
            f"ID: {self.trans_id}, Queries: {self.queries_count}, "
            f"Answers: {self.answers_count}, Authoritative: "
            f"{self.auth_count}, Additionals: {self.additional_count}"
        )
