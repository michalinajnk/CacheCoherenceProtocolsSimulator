import abc
from io import StringIO

class Trace(abc.ABC):
    """
    Abstract base class for all instructions.
    """
    def __init__(self, address=None):
        self.address = address

    @abc.abstractmethod
    def execute(self, cache):
        """
        Execute the instruction with respect to the provided cache.
        """
        pass

    @abc.abstractmethod
    def detect(self, cache):
        """
        Detect if the instruction can proceed based on cache state.
        """
        pass

    @staticmethod
    def create_instruction(line):
        """
        Factory method to create specific instruction types based on input data.
        """
        iss = StringIO(line)
        instruction_type, hexval = map(int, iss.readline().split())
        if instruction_type == 0:
            return Instruction0(hexval)
        elif instruction_type == 1:
            return Instruction1(hexval)
        elif instruction_type == 2:
            return Instruction2(hexval)
        else:
            raise ValueError("Unknown instruction type")

class Instruction0(Trace):
    def execute(self, cache):
        return cache.read_addr(self.address)

    def detect(self, cache):
        return cache.detect_addr(self.address)

class Instruction1(Trace):
    def execute(self, cache):
        return cache.write_addr(self.address)

    def detect(self, cache):
        return cache.detect_addr(self.address, True)

class Instruction2(Trace):
    def __init__(self, time):
        super().__init__(None)
        self.time = time

    def execute(self, cache):
        return self.time

    def detect(self, cache):
        return self.time
