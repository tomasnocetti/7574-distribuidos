BASE_LENGTH_MESSAGE = 3
ALIVE_MESSAGE = 'LM'
ANSWER_MESSAGE = 'AM'
COORDINATOR_MESSAGE = 'CM'
LEADER_ELECTION_MESSAGE = 'EM'

class ElectionMessage:
    def __init__(self, type: str, id: int) -> None:
        self.CODE = None
        self.type = type
        self.id = id

    def pack(self):
        return f'{self.CODE}'

    @staticmethod
    def of(message: str):
        split = message.split("_")
        return ElectionMessage(split[0], int(split[1]))

    def to_string(self) -> str:
        return self.type + "_" + str(self.id)

class AliveMessage(ElectionMessage):
    def __init__(self, id) -> None:
        super().__init__(ALIVE_MESSAGE, id)
        self.CODE = ALIVE_MESSAGE
    
    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == ALIVE_MESSAGE

class AnswerMessage(ElectionMessage):
    def __init__(self, id) -> None:
        super().__init__(ANSWER_MESSAGE, id)
        self.CODE = ANSWER_MESSAGE
    
    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == ANSWER_MESSAGE

class LeaderElectionMessage(ElectionMessage):
    def __init__(self, id) -> None:
        super().__init__(LEADER_ELECTION_MESSAGE, id)
        self.CODE = LEADER_ELECTION_MESSAGE

    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == LEADER_ELECTION_MESSAGE

class CoordinatorMessage(ElectionMessage):
    def __init__(self, id) -> None:
        super().__init__(COORDINATOR_MESSAGE, id)
        self.CODE = COORDINATOR_MESSAGE

    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == COORDINATOR_MESSAGE