ELECTION_LENGTH_MESSAGE = 4 #ELECTION BASE MESSAGE HAS 'XXX_' FORMAT

ALIVE_MESSAGE = 'ALM'
LEADER_ELECTION_MESSAGE = 'LEM'
COORDINATOR_MESSAGE = 'COM'

ALIVE_ANSWER_MESSAGE = 'AAM'
ELECTION_ANSWER_MESSAGE = 'EAM'

TIMEOUT_MESSAGE = 'TOM'
ERROR_MESSAGE = 'ERM'

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

class AliveAnswerMessage(ElectionMessage):
    def __init__(self, id) -> None:
        super().__init__(ALIVE_ANSWER_MESSAGE, id)
        self.CODE = ALIVE_ANSWER_MESSAGE
    
    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == ALIVE_ANSWER_MESSAGE

class ElectionAnswerMessage(ElectionMessage):
    def __init__(self, id) -> None:
        super().__init__(ELECTION_ANSWER_MESSAGE, id)
        self.CODE = ELECTION_ANSWER_MESSAGE
    
    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == ELECTION_ANSWER_MESSAGE

class TimeoutMessage(ElectionMessage):
    def __init__(self) -> None:
        super().__init__(TIMEOUT_MESSAGE, -1)
        self.CODE = TIMEOUT_MESSAGE

    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == TIMEOUT_MESSAGE

class ErrorMessage(ElectionMessage):
    def __init__(self) -> None:
        super().__init__(ERROR_MESSAGE, -1)
        self.CODE = ERROR_MESSAGE

    @staticmethod
    def is_election(election: ElectionMessage) -> bool:
        return election.type == ERROR_MESSAGE