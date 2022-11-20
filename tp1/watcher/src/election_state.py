PARTICIPATING = 'P'
NOT_PARTICIPATING = 'NP'

class ElectionState:
    def __init__(self) -> None:
        self.CODE = None

class Participating(ElectionState):
    def __init__(self) -> None:
        self.CODE = PARTICIPATING
    
    @staticmethod
    def is_state(state: ElectionState) -> bool:
        return state.CODE == PARTICIPATING

class NotParticipating(ElectionState):
    def __init__(self) -> None:
        self.CODE = NOT_PARTICIPATING
    
    @staticmethod
    def is_state(state: ElectionState) -> bool:
        return state.CODE == NOT_PARTICIPATING