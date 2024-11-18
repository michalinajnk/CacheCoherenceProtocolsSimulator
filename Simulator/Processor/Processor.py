import os
from Simulator.Cache.Cache import Cache
from Simulator.Configuration.Trace import Trace
from .Observer import Observer
import threading
import logging

class Processor(Observer):
    def __init__(self, processor_id, trace_file_name, config, root_path):
        logging.debug("Initializing Processor with ID %s", processor_id)
        self.id = processor_id
        self.halt_cycles = 0
        self.trace_file_path = os.path.join(root_path, f"{trace_file_name}{processor_id}.data")
        self.cache = Cache(config, processor_id)
        self.current_instruction = None
        self.currently_processing_instructions = set()
        self.trace_file = None
        self.state_lock = threading.Lock()
        self.instruction_lock = threading.Lock()
        self.config = config

        try:
            self.trace_file = open(self.trace_file_path, 'r')
            logging.info("Successfully opened trace file: %s", self.trace_file_path)
        except IOError:
            logging.error("Failed to open trace file: %s", self.trace_file_path)
            raise

    def update(self, current_cycle):
        logging.debug("Updating processor state for cycle %s", current_cycle)
        if self.halt_cycles == 0:
            if self.current_instruction is not None:
                with self.instruction_lock:
                    address = self.cache.parse_address(self.current_instruction.get_value())
                    if address in self.currently_processing_instructions:
                        self.config.CPU_STATS[self.id].increment("idle_cycles")
                        return True
                    else:
                        self.currently_processing_instructions.add(address)
                        self.halt_cycles = self.current_instruction.detect(self.cache)
                        self.halt_cycles -= 1
                        self.config.CPU_STATS[self.id].increment("idle_cycles")
                        if self.halt_cycles == 0 and self.current_instruction is not None:
                            self.current_instruction.execute(self.cache)
                            self.currently_processing_instructions.remove(address)
                            self.current_instruction = None
                        return True

            fetched_instruction = self.fetch_instruction()
            if fetched_instruction:
                if self.process_instruction(fetched_instruction):
                    return True  # If instruction was processed, update can conclude successfully for this cycle

        with self.instruction_lock:
            self.halt_cycles -= 1
            self.config.CPU_STATS[self.id].increment("idle_cycles")
            if self.halt_cycles == 0 and self.current_instruction is not None:
                self.execute_instruction()
                if isinstance(self.current_instruction, Trace) and self.current_instruction.identify() in [0, 1]:
                    address = self.cache.parse_address(self.current_instruction.get_value())
                    assert address in self.currently_processing_instructions
                    self.currently_processing_instructions.remove(address)
                self.current_instruction = None
                return True

        logging.debug(f"Cpu {self.id} has finished at cycle {current_cycle} ")
        self.config.CPU_STATS[self.id].set_count("sum_execution_time", current_cycle)
        self.trace_file.close()
        return False

    def fetch_instruction(self):
        line = self.trace_file.readline()
        if not line:
            self.trace_file.close()
            logging.info("No more instructions; closing file")
        else:
            logging.debug("Fetched instruction: %s", self.current_instruction)
            return Trace.create_instruction(line)

    def process_instruction(self, fetched_instruction):
        with self.instruction_lock:
            if fetched_instruction.identify() in [0,1] :
                if fetched_instruction == 0:
                    self.config.CPU_STATS[self.id].increment("load_number")
                else:
                    self.config.CPU_STATS[self.id].increment("store_number")
                address = self.cache.parse_address(fetched_instruction.get_value())
                if address in self.currently_processing_instructions:
                    logging.debug("Address %s is currently being processed; skipping", address)
                    self.halt_cycles = 0
                    self.current_instruction = fetched_instruction
                    self.config.CPU_STATS[self.id].increment("idle_cycles")
                    return True
                self.currently_processing_instructions.add(address)
                logging.info("Processing new instruction at address %s", address)
            else:
                self.config.CPU_STATS[self.id].add_many("compute_cycles",fetched_instruction.get_value())
            self.halt_cycles = fetched_instruction.detect(self.cache)
            self.current_instruction = fetched_instruction
            self.halt_cycles -= 1
            self.config.CPU_STATS[self.id].increment("idle_cycles")
            if self.halt_cycles == 0 and self.current_instruction is not None:
                executed = self.execute_instruction()
                if self.current_instruction.identify() in [0,1]:
                    address = self.cache.parse_address(self.current_instruction.get_value())
                    if address in self.currently_processing_instructions:
                        self.currently_processing_instructions.remove(address)
                self.current_instruction = None
            return True


    def execute_instruction(self):
        result = self.current_instruction.execute(self.cache)
        return result

    def __del__(self):
        if self.trace_file and not self.trace_file.closed:
            self.trace_file.close()
            logging.info("Trace file closed on processor destruction")

    def set_halt_cycles(self, halt):
        with self.state_lock:
            logging.debug("Setting halt cycles to %s", halt)
            self.halt_cycles = halt

    def set_instruction(self, instruction):
        with self.state_lock:
            logging.debug("Setting new instruction")
            self.current_instruction = instruction

    def get_instruction(self):
        return self.current_instruction

