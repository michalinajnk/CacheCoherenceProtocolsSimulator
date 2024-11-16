from abc import ABC, abstractmethod

class CacheProtocol(ABC):
    """
    Abstract base class for cache coherence protocols, defining methods to process messages
    and identify the protocol type.
    """
    def __init__(self):
        self.int_to_state_map = {}

    @abstractmethod
    def process_msg(self, msg, flags, caches):
        """
        Process a message within the coherence protocol.

        Args:
            msg (Message): The message being processed.
            flags (list[bool]): A list of boolean flags indicating the distribution of cached copies.
            caches (list[CacheLine]): A list of CacheLine instances that hold a copy of the data.

        Returns:
            int: The time in cycles to stay on the bus.
        """
        pass

    @abstractmethod
    def get_protocol(self):
        """
        Identify the type of the coherence protocol.

        Returns:
            int: An identifier for the type of protocol.
        """
        pass
