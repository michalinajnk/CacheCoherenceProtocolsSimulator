from Simulator.StateMachine.states import InvalidState, ModifiedState, ExclusiveState, SharedState, OwnedState


class StateHandler:
    """
    Provides access to the singleton instances of MESI protocol states.
    """
    @staticmethod
    def invalid():
        return InvalidState()

    @staticmethod
    def modified():
        return ModifiedState()

    @staticmethod
    def exclusive():
        return ExclusiveState()

    @staticmethod
    def shared():
        return SharedState()

    @staticmethod
    def owned():
        return OwnedState()
