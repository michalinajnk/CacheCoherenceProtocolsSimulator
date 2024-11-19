import threading

from Simulator.Cache.MessageType import MessageType


class CacheController:
    """
    Controls interactions between a cache and its associated bus, handling requests and replies.
    """


    def __init__(self, identifier, bus, cache):
        """
        Initializes the CacheController with identifiers and connections to a bus and a cache.

        Args:
            identifier (int): Unique identifier for the controller.
            bus (Bus): The bus instance to which the controller will send requests.
            cache (Cache): The cache instance that this controller will manage.
        """
        self.identifier = identifier
        self.bus = bus
        self.cache = cache
        self.lock = threading.Lock()

    def get_id(self):
        """
        Returns the identifier of the controller.

        Returns:
            int: The controller's identifier.
        """
        with self.lock:
            return self.identifier

    def get_line_if_present(self, address):
        """
        Retrieves a line from the cache if it is present, without modifying it.
        """
        index = address.set_index
        cache_set = self.cache.sets[index]
        line = cache_set.is_hit_msg(address.tag)
        return line

    def send_request(self, message):
        """
        Sends a request through the bus.

        Args:
            message (Message): The message to send.
        """
        with self.lock:
            self.bus.send_request(message)


    def receive_reply(self, message):
        """
        Processes a received reply message, handling any necessary cache or processor operations.

        Args:
            message (Message): The received reply message.
        """
        flag = self.cache.get_cache_sets()[message.address.set_index].need_write_back(message.address)
        if flag:
            self.cache.processor.set_halt_cycles(self.cache.time_config.write_back_mem)
        else:
            self.cache.processor.set_halt_cycles(0)
            self.cache.processor.get_instruction().execute(self.cache)


        if message.message_type == MessageType.READ_REQ:
            # Fetch the data as part of handling a read request
            self.update_cache(message.address, is_write=False)
        elif message.message_type == MessageType.WRITE_REQ:
            self.update_cache(message.address, is_write=True)

        # Clearing the processor's current instruction
        if self.cache.processor.get_instruction() and self.cache.processor.get_instruction().identify() == 0:
            parse = self.cache.parse_address(self.cache.processor.get_instruction().get_value())
            if  parse in self.cache.get_instructions():  # Ensure the instruction is present
                self.cache.get_instructions().remove(parse)
            self.cache.processor.set_instruction(None)

    def update_cache(self, address, is_write):
        """
        Updates the cache line with the new data fetched from memory.
        """
        set_index, tag = self.cache.parse_address(address.to_physical_address(self.cache.block_size, len(self.cache.get_cache_sets())))
        cache_set = self.cache.sets[set_index]
        cache_set.add_or_replace_line(tag, is_write)

