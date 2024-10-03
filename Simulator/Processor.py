from Cache import Cache

from typing import Union

class Processor:
    def __init__(self):
        
        self.cache = Cache(cache_size=1024, block_size=16, associativity=1)
        self.clock = 0
        return None
    
    
    def update_clock(self, cycles = 1):
        """
        Updates the processor's clock by a specified number of cycles.
        Args:
            cycles (int, optional): The number of cycles to increment the clock by. Defaults to 1.
        Returns:
            None
        """
        self.clock += cycles
        return None
    
    def get_clock(self):
        """
        Returns the current clock cycle of the processor.
        Returns:
            int: The current clock cycle.
        """
        return self.clock

    def parse_instruction(self, label: int , value: Union[str, int]):
        '''
        ## label:
            - `0`: read
            - `1`: write
            - `2`: other instructions (add, sub, etc.) (only appear between two read/write instructions)
        ## value: 
            - for read/write instructions: memory address
            - for other instructions: denotes clock cycles required by other instructions between two memory access operations (load/store instructions).
        '''
        
        match label:
            case 0:
                # read value from memory
                self.update_clock(self.cache.access(value, is_write=False))
                return 
                pass
            case 1:
                # write instruction
                self.update_clock(self.cache.access(value, is_write=True))
                pass
            case 2:
                # other instructions
                self.update_clock(int(value, 16))
                pass