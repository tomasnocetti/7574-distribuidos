LEADER = 'L'
LEADER_ELECTION = 'LE'
LEADER_SELECTED = 'LS'

class Election:
    def __init__(self, type: str, id: int) -> None:
        self.CODE = None
        self.type = type
        self.id = id

    def pack(self):
        return f'{self.CODE}'

    @staticmethod
    def of(message: str):
        split = message.split("_")
        return Election(split[0], int(split[1]))

    def to_string(self) -> str:
        return self.type + "_" + str(self.id)

class Leader(Election):
    def __init__(self, id) -> None:
        super().__init__(LEADER, id)
        self.CODE = LEADER
    
    @staticmethod
    def is_election(election: Election) -> bool:
        return election.type == LEADER

class LeaderElection(Election):
    def __init__(self, id) -> None:
        super().__init__(LEADER_ELECTION, id)
        self.CODE = LEADER_ELECTION

    @staticmethod
    def is_election(election: Election) -> bool:
        return election.type == LEADER_ELECTION

class LeaderSelected(Election):
    def __init__(self, id) -> None:
        super().__init__(LEADER_SELECTED, id)
        self.CODE = LEADER_SELECTED

    @staticmethod
    def is_election(election: Election) -> bool:
        return election.type == LEADER_SELECTED