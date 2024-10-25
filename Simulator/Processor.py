from Cache import Cache
import Constants

from typing import Union

class Processor:
    def __init__(self, cache, BUS, DATALOADER):
        
        self.cache = cache
        self.exicuteCycle = 0
        self.BUS = BUS
        self.DATALOADER = DATALOADER
        self.STATUS = None
        
        # clock cycle
        self.idle_cycles = 0
        self.compute_cycles = 0
        
        # status flag
        self.stalled = False
        self.stall_cycles = 0
        self.completed = False
        self.instruction = None
        
        # counters
        self.load_count = 0
        self.store_count = 0
        
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
    
    def print_stats(self, totalCycles):
        """
        Prints the statistics of the processor.
        Returns:
            None
        """
        totalInstructions = self.DATALOADER.getInstructionCount()
        print(f"Number of load instructions: {self.load_count} ({self.load_count/totalInstructions*100:.2f}%)")
        print(f"Number of store instructions: {self.store_count} ({self.store_count/totalInstructions*100:.2f}%)")
        print(f"Number of idle cycles: {self.idle_cycles} ({self.idle_cycles/totalCycles*100:.2f}%)")
        print(f"Number of compute cycles: {self.compute_cycles} ({self.compute_cycles/totalCycles*100:.2f}%)")
        return None

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
                needToWait = self.cache.access(value, is_write=False)
                if needToWait >=1:
                    self.STATUS = Constants.ProcessorStatus.IDEL
                    self.stall_cycles = needToWait
                    self.stalled = True
                self.load_count += 1
                pass
            case 1:
                # write instruction
                needToWait = self.cache.access(value, is_write=True)
                if needToWait >=1:
                    self.STATUS = Constants.ProcessorStatus.IDEL
                    self.stall_cycles = needToWait
                    self.stalled = True
                self.store_count += 1
                pass
            case 2:
                # other instructions
                # need to stall the processor for `value` cycles
                self.STATUS = Constants.ProcessorStatus.COMPUTE
                self.stall_cycles = int(value,16)
                self.stalled = True
                pass
            
    def nextTick(self):
        self.exicuteCycle += 1
        if not self.stalled and (self.stall_cycles == 0):
            # parse the next instruction
            self.instruction = self.DATALOADER.getInstruction()
            if self.instruction is not None:
                self.parse_instruction(self.instruction[0], self.instruction[1])
            else:
                # instruction is None, simulation is completed
                self.completed = True
                
            
        elif self.STATUS == Constants.ProcessorStatus.COMPUTE:
            self.stall_cycles -= 1
            if self.stall_cycles == 0:
                self.stalled = False
            self.compute_cycles += 1
        elif self.STATUS == Constants.ProcessorStatus.IDEL:
            self.stall_cycles -= 1
            if self.stall_cycles == 0:
                self.stalled = False
            self.idle_cycles += 1
        else:
            print("Unknown status")
            
            