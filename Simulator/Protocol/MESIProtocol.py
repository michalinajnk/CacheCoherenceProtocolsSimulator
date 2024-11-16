
from Simulator.Cache.MessageType import MessageType
from Simulator.Protocol.CacheProtocol import CacheProtocol
from Simulator.StateMachine.StateHandler import StateHandler


class MESIProtocol(CacheProtocol):
    """
    MESI Cache Coherence Protocol implementation in Python.
    Handles the specific logic of the MESI protocol for cache coherence.
    """

    def __init__(self, config):
        super().__init__()
        self.cpu_stats = config.CPU_STATS
        self.CPU_NUMS = config.CPU_NUMS
        self.CACHE_CONFIG = config.CACHE_CONFIG
        self.TIME_CONFIG = config.TIME_CONFIG

    def get_protocol(self):
        """
        Identify the protocol type.
        """
        return 0  # MESI protocol identifier

    def process_msg(self, msg, flags, caches):
        """
        Process a message in the context of the MESI cache coherence protocol.
        """
        cnt = sum(flags)  # Count how many caches hold a copy

        # Check if there is a modified state in any cache
        flag = any(flags[i] and caches[i].get_state() == StateHandler.modified() for i in range(self.CPU_NUMS))

        if not flags[msg.sender_id]:  # Start from Invalid State
            if msg.message_type == MessageType.WRITE_REQ:
                if cnt == 0:
                    self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                else:
                    # Transition to Modified requires invalidation of other caches
                    for i in range(self.CPU_NUMS):
                        if flags[i]:
                            caches[i].set_state(StateHandler.invalid())
                            caches[i].set_valid(False)
                    self.int_to_state_map[msg.sender_id] = StateHandler.modified()
                    self.cpu_stats[self.CPU_NUMS]['data_traffic'] += self.CACHE_CONFIG.block_size
                    self.cpu_stats[self.CPU_NUMS]['invalidation'] += 1
                    return self.CACHE_CONFIG.block_size // 2
            else:  # READ_REQ
                if cnt == 0:
                    self.int_to_state_map[msg.sender_id] = StateHandler.exclusive()
                elif cnt == 1 and flag:
                    # Transition from Modified to Shared
                    for i in range(self.CPU_NUMS):
                        if flags[i]:
                            caches[i].set_state(StateHandler.shared())
                            caches[i].set_dirty(False)  # Reset the dirty bit if Modified
                    self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                    return max(self.CACHE_CONFIG.block_size // 2, self.TIME_CONFIG.write_back_mem)
                else:
                    # All other caches must also transition to Shared
                    for i in range(self.CPU_NUMS):
                        if flags[i]:
                            caches[i].set_state(StateHandler.shared())
                    self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                    self.cpu_stats[self.CPU_NUMS]['data_traffic'] += self.CACHE_CONFIG.block_size
                    return self.CACHE_CONFIG.block_size // 2

        # For already flagged senderId with WRITE_REQ
        elif flags[msg.sender_id] and msg.message_type == MessageType.WRITE_REQ:
            if cnt == 1:
                # Exclusive or Shared to Modified directly
                caches[msg.sender_id].set_state(StateHandler.modified())
            else:
                # Invalidate others if Shared to Modified
                for i in range(self.CPU_NUMS):
                    if i != msg.sender_id and flags[i]:
                        caches[i].set_state(StateHandler.invalid())
                        caches[i].set_valid(False)
                caches[msg.sender_id].set_state(StateHandler.modified())
                self.cpu_stats[self.CPU_NUMS]['invalidation'] += 1

        return 0  # No additional delay