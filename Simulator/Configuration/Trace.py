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

    @abc.abstractmethod
    def identify(self):
        pass

    def get_value(self):
        return self.address

    @staticmethod
    def create_instruction(line):
        """
        Factory method to create specific instruction types based on input data.
        """
        iss = StringIO(line)
        instruction_type, hexval = iss.readline().split()
        instruction_type = int(instruction_type)
        hexval = int(hexval, 16)  # Specify base 16 for hexadecimal

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
        return cache.read_address(self.address)

    def identify(self):
        return 0

    def detect(self, cache):
        return cache.detect_address(self.address)


class Instruction1(Trace):
    def execute(self, cache):
        return cache.write_address(self.address)

    def identify(self):
        return 1

    def detect(self, cache):
        return cache.detect_address(self.address, True)



class Instruction2(Trace):
    def __init__(self, time):
        super().__init__(None)
        self.time = time

    def identify(self):
        return 2
    
    def get_value(self):
        return self.time

    def execute(self, cache):
        return self.time

    def detect(self, cache):
        return self.time
