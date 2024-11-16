from queue import Queue
from collections import deque

class Bus:
    def __init__(self, coherence_protocol):
        self.caches = []
        self.request_messages = Queue()
        self.reply_messages = Queue()
        self.coherence_protocol = coherence_protocol

    def register_cache(self, cache_controller):
        """
        Registers a cache controller to the bus.
        Args:
            cache_controller (CacheController): The cache controller to be registered.
        """
        self.caches.append(cache_controller)

    def send_request(self, message):
        """
        Adds a request message to the queue to be processed.
        Args:
            message (Message): The message to be sent as a request.
        """
        self.request_messages.put(message)

    def send_reply(self, message):
        """
        Adds a reply message to the queue to be processed.
        Args:
            message (Message): The message to be sent as a reply.
        """
        self.reply_messages.put(message)

    def propagate_requests(self):
        """
        Process all request messages in the queue, simulating bus interactions and cache coherency mechanisms.
        """
        while not self.request_messages.empty():
            message = self.request_messages.get()
            flags = [False] * len(self.caches)  # caches hold a copy or not
            cache_lines = [None] * len(self.caches)  # CacheLine objects from each cache

            # Collect information about caches that hold a copy
            for i, cache in enumerate(self.caches):
                cache_line = cache.get_line_if_present(message.address)
                cache_lines[i] = cache_line
                if cache_line is not None:
                    flags[i] = True
            #decide new states and apply changes
            response_time = self.coherence_protocol.process_msg(message, flags, cache_lines)
            message.stay_in_bus = response_time

            #calculate time in bus before sending reply
            message.stay_in_bus -= 1
            if message.stay_in_bus > 0:
                self.request_messages.put(message)  # Requeue if more time needed
            else:
                self.send_reply(message)  # Send reply if done

    def propagate_replies(self):
        """
        Process all reply messages in the queue, notifying the corresponding cache controller about completion.
        """
        while not self.reply_messages.empty():
            message = self.reply_messages.get()
            # Notify the cache controller that the operation is completed
            for cache in self.caches:
                if cache.get_id() == message.sender_id:
                    cache.receive_reply(message)
