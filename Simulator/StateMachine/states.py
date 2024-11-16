from Simulator.StateMachine.State import State


class InvalidState(State):
    """
    Singleton implementation of the InvalidState.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_state_name(self):
        return "Invalid"


class ModifiedState(State):
    """
    Singleton implementation of the ModifiedState.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_state_name(self):
        return "Modified"

class OwnedState(State):
    """
    Singleton implementation of the OwnedState.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_state_name(self):
        return "Owned"


class ExclusiveState(State):
    """
    Singleton implementation of the ExclusiveState.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_state_name(self):
        return "Exclusive"


class SharedState(State):
    """
    Singleton implementation of the SharedState.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def get_state_name(self):
        return "Shared"