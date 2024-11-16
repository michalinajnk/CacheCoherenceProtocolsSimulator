
from enum import Enum, auto

class MessageType(Enum):
    READ_REQ = auto()
    WRITE_REQ = auto()

class Message:
    def __init__(self, sender_id, stay_in_bus, address, message_type):
        self.sender_id = sender_id
        self.stay_in_bus = stay_in_bus
        self.address = address
        self.message_type = message_type
