import os

from Simulator.Cache.Cache import Cache
from Simulator.Configuration.Trace import Trace
from Simulator.Processor.Observer import Observer


class Processor(Observer):
    """
    Simulates a processor which processes instructions and interacts with a cache.
    """
    def __init__(self, processor_id, trace_file_name, cache_configuration, timing_configuration, root_path):
        self.id = processor_id
        self.halt_cycles = 0
        self.trace_file_path = os.path.join(root_path, f"{trace_file_name}{processor_id}.data")
        self.cache = Cache(cache_configuration,timing_configuration)
        self.timing = timing_configuration
        self.current_instruction = None
        self.insts = set()  # Manage unique instructions being processed
        try:
            self.trace_file = open(self.trace_file_path, 'r')
        except IOError:
            print(f"Failed to open file {self.trace_file_path}")
            raise

    def update(self, current_cycle):
        if self.halt_cycles > 0:
            self.halt_cycles -= 1
            if self.halt_cycles == 0 and self.current_instruction:
                self.execute_instruction()
            return True

        if not self.current_instruction:
            line = self.trace_file.readline()
            if not line:
                self.trace_file.close()
                return False
            self.current_instruction = Trace.create_instruction(line)

        self.process_instruction()
        return True

    def execute_instruction(self):
        if self.current_instruction:
            result = self.current_instruction.execute(self.cache)
            if result:
                address = self.cache.parse_address(self.current_instruction.get_val())
                self.insts.remove(address)
            self.current_instruction = None

    def process_instruction(self):
        address = self.cache.parse_address(self.current_instruction.get_val())
        if address in self.insts:
            self.halt_cycles = 0
        else:
            self.insts.add(address)
            self.halt_cycles = self.current_instruction.detect(self.cache, self.timing)
            self.halt_cycles -= 1

    def __del__(self):
        if self.trace_file and not self.trace_file.closed:
            self.trace_file.close()