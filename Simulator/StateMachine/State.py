import abc


class State(abc.ABC):
    """
    Base class for all states. This is an abstract class meant to be extended by specific states.
    """

    def get_state_name(self):
        """
        Returns the name of the state.
        """
        pass