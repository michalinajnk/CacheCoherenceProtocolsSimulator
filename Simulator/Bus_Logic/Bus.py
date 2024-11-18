import logging
from queue import Queue

class Bus:
    def __init__(self, coherence_protocol, config):
        self.cache_controllers = []
        self.request_messages = Queue()
        self.reply_messages = Queue()
        self.config = config
        self.coherence_protocol = coherence_protocol

    def register_cache(self, cache_controller):
        self.cache_controllers.append(cache_controller)

    def send_request(self, message):
        self.request_messages.put(message)

    def send_reply(self, message):
        self.reply_messages.put(message)

    def propagate_requests(self):
        while not self.request_messages.empty():
            message = self.request_messages.get()
            flags = [False] * len(self.cache_controllers)
            cache_lines = [None] * len(self.cache_controllers)
            if message.stay_in_bus == -1:
                message.stay_in_bus = self.config.TIME_CONFIG.cache_hit 

                for i, cache_controller in enumerate(self.cache_controllers):
                    cache_lines[i] = cache_controller.cache.get_cache_sets()[message.address.set_index].is_hit_msg(message.address.tag)
                    if cache_lines[i] is not None:
                        flags[i]  = True

                message.stay_in_bus += self.coherence_protocol.process_msg(message, flags, cache_lines)
            message.stay_in_bus -=1
            self.send_reply(message)




    def propagate_replies(self):
        while not self.reply_messages.empty():
            message = self.reply_messages.get()
            if message.stay_in_bus != 0:
                self.send_request(message)
            else:
                for cache in self.cache_controllers:
                    if cache.get_id() == message.sender_id:
                        logging.debug(f"Processing reply for cache {cache.get_id()}")
                        cache.receive_reply(message)