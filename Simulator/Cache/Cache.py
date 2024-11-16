import math
from Simulator.Cache.CacheAddress import CacheAddress
from Simulator.Cache.CacheSet import CacheSet
from Simulator.Cache.MessageType import Message, MessageType


class Cache:
    """
    Manages a fully associative cache simulation, including read and write operations
    and interfacing with a controller for cache coherence.
    """

    def __init__(self, config, time_config):
        """
        Initializes the Cache with specific configurations.

        Args:
            config (CacheConfig): Configuration object containing cache size, block size, etc.
            time_config (TimeConfig): Configuration object containing timing related configurations.
        """
        self.identifier = config.identifier
        self.total_size = config.cache_size
        self.block_size = config.block_size
        self.associativity = config.associativity
        self.set_count = self.total_size // (self.block_size * self.associativity)
        self.sets = [CacheSet(self.associativity, self.identifier) for _ in range(self.set_count)]
        self.controller = None
        self.processor = None
        self.time_config = time_config

    def parse_address(self, address):
        """
        Parses the physical address to obtain the cache set index and tag.

        Args:
            address (int): The physical memory address to parse.

        Returns:
            tuple: Contains set_index (int) and tag (int).
        """
        block_offset_bits = int(math.log2(self.block_size))
        set_index_bits = int(math.log2(self.set_count))
        set_index_mask = ((1 << set_index_bits) - 1) << block_offset_bits
        set_index = (address & set_index_mask) >> block_offset_bits
        tag = address >> (block_offset_bits + set_index_bits)
        return set_index, tag

    def read_address(self, address):
        """
        Processes a read operation for the given address.

        Args:
            address (int): Memory address to read from.

        Returns:
            int: Timing result based on cache hit or miss.
        """
        set_index, tag = self.parse_address(address)
        cache_set = self.sets[set_index]
        line = cache_set.find_line(tag)
        if line:
            return self.time_config.cache_hit
        else:
            cache_set.load_line(tag, False)
            return self.time_config.cache_hit + self.time_config.load_block_from_mem

    def write_address(self, address):
        """
        Processes a write operation for the given address.

        Args:
            address (int): Memory address to write to.

        Returns:
            int: Timing result based on cache hit or miss.
        """
        set_index, tag = self.parse_address(address)
        cache_set = self.sets[set_index]
        line = cache_set.find_line(tag)
        if line:
            line.is_dirty = True
            return self.time_config.cache_hit
        else:
            cache_set.load_line(tag, True)
            return self.time_config.cache_hit + self.time_config.write_back_mem

    def detect_address(self, address, is_write=False):
        """
        Detects if the address is in cache, if not, sends a bus request.

        Args:
            address (int): The address to check.
            is_write (bool): Indicates if the operation is a write.

        Returns:
            float: Simulated result of the operation.
        """
        set_index, tag = self.parse_address(address)
        cache_set = self.sets[set_index]
        line = cache_set.find_line(tag)

        if line:
            if is_write and not line.is_dirty:
                message = Message(sender_id=self.identifier, stay_in_bus=-1,
                                  address=CacheAddress(tag, set_index), message_type=MessageType.WRITE_REQ)
                self.controller.send_request(message)
                return float('inf')  # Simulating std::numeric_limits<int>::max()
            return self.time_config.cache_hit
        else:
            message = Message(sender_id=self.identifier, stay_in_bus=-1,
                              address=CacheAddress(tag, set_index),
                              message_type=MessageType.WRITE_REQ if is_write else MessageType.READ_REQ)
            self.controller.send_request(message)
            return float('inf')

    def set_controller(self, controller):
        """
        Sets the cache's controller.

        Args:
            controller (CacheController): The controller to set.
        """
        self.controller = controller

    def set_processor(self, processor):
        """
        Sets the processor associated with this cache.

        Args:
            processor (CPU): The processor to set.
        """
        self.processor = processor

    def get_sets(self):
        """
        Returns the list of cache sets.

        Returns:
            list: The list of CacheSet objects.
        """
        return self.sets
