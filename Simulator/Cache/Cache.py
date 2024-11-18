import math
from Simulator.Cache.CacheAddress import CacheAddress
from Simulator.Cache.CacheSet import CacheSet
from Simulator.Cache.MessageType import Message, MessageType
import logging

class Cache:
    """
    Manages a fully associative cache simulation, including read and write operations
    and interfacing with a controller for cache coherence.
    """

    def __init__(self, config, identifier):
        self.config = config
        self.identifier = identifier
        self.total_size = config.CACHE_CONFIG.cache_size
        self.block_size = config.CACHE_CONFIG.block_size
        self.associativity = config.CACHE_CONFIG.associativity
        self.set_count = self.total_size // (self.block_size * self.associativity)
        self.sets = [CacheSet(config, self.associativity, self.identifier) for _ in range(self.set_count)]
        self.time_config = config.TIME_CONFIG
        logging.debug("Cache initialized with ID %s, Total Size %s, Block Size %s, Associativity %s, Set Count %s",
                      identifier, self.total_size, self.block_size, self.associativity, self.set_count)

    def parse_address(self, address: int) -> tuple:
        block_offset_bits = int(math.log2(self.block_size))
        set_index_bits = int(math.log2(self.set_count))
        set_index_mask = ((1 << set_index_bits) - 1) << block_offset_bits
        set_index = (address & set_index_mask) >> block_offset_bits
        tag = address >> (block_offset_bits + set_index_bits)
        logging.debug(f"Parsed address {address} to (Set Index: {set_index}, Tag: {tag})")
        return set_index, tag

    def read_address(self, address):
        set_index, tag = self.parse_address(address)
        cache_set = self.sets[set_index]
        line = cache_set.is_hit(tag)
        if line:
            logging.info(f"Cache hit for address {address} at set {set_index}, tag {tag}")
            return self.time_config.cache_hit
        else:
            logging.warning(f"Cache miss for address {address}; loading line")
            return self.time_config.cache_hit + cache_set.load_line(tag, False)

    def write_address(self, address):
        set_index, tag = self.parse_address(address)
        cache_set = self.sets[set_index]
        line = cache_set.is_hit(tag, True)
        if line:
            logging.info(f"Write hit for address {address}; setting line to dirty")
            line.set_dirty(True)
            return self.time_config.cache_hit
        else:
            logging.warning(f"Write miss for address {address}; loading line")
            return self.time_config.cache_hit + cache_set.load_line(tag, True)



    def detect_address(self, address, is_write=False):
        set_index, tag = self.parse_address(address)
        cache_set = self.sets[set_index]
        line = cache_set.is_hit_readonly(tag, is_write)
        if line:
            logging.info(f"Address {address} detected in cache; no further action needed")
            return self.time_config.cache_hit
        else:
            logging.warning(f"Address {address} not found in cache; sending bus request")
            message_type = MessageType.WRITE_REQ if is_write else MessageType.READ_REQ
            message = Message(sender_id=self.controller.identifier, stay_in_bus=-1,
                              address=CacheAddress(tag, set_index), message_type=message_type)
            self.controller.send_request(message) #lock
            return float('inf')  # Simulates an indefinite delay or very high cost


    def set_controller(self, controller):
        logging.debug(f"Setting controller for Cache ID {self.identifier}")
        self.controller = controller

    def set_processor(self, processor):
        logging.debug(f"Setting processor for Cache ID {self.identifier}")
        self.processor = processor

    def get_sets(self):
        return self.sets

    def get_instructions(self):
        return self.config.instructions

    def set_instructions(self, instruction):
        logging.debug(f"Setting new instructions for Cache ID {self.identifier}")
        self.config.instructions = instruction
