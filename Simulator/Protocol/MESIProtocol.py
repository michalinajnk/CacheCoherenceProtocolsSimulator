import logging

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
        has_modified = any(
            flags[i] and caches[i] is not None and caches[i].state == StateHandler.modified() for i in
            range(self.CPU_NUMS))

        if not flags[msg.sender_id]:  # Start from Invalid State
            #assert not msg.sender_id in self.int_to_state_map.keys()
            if msg.message_type == MessageType.WRITE_REQ:
                if cnt == 0:
                    self.int_to_state_map[msg.sender_id] = StateHandler.modified()
                elif cnt == 1:
                    # Transition to Modified requires invalidation of other caches
                    empty_cache = 0
                    for i in range(self.CPU_NUMS):
                        if flags[i] and caches[i]:
                            cnt -= 1
                            if has_modified:
                                assert caches[i].state == StateHandler.modified()

                            caches[i].state = StateHandler.invalid()
                            caches[i].valid = False
                        elif not caches[i]:
                            empty_cache+=1

                    cnt = max(0, self.CPU_NUMS - empty_cache)
                    assert cnt == 0
                    logging.debug(f"Number of cache copies: {cnt}")
                    self.int_to_state_map[msg.sender_id] = StateHandler.invalid()
                    self.cpu_stats[self.CPU_NUMS].add_many('data_traffic', self.CACHE_CONFIG.block_size)
                    self.cpu_stats[self.CPU_NUMS].increment('invalidation')
                    return self.CACHE_CONFIG.block_size // 2
                else:
                    assert not has_modified
                    for i in range(self.CPU_NUMS):
                        if flags[i] and caches[i]:
                            cnt -= 1
                            assert caches[i].state == StateHandler.shared()
                            caches[i].state = StateHandler.invalid()
                            caches[i].valid = False
                    assert cnt == 0
                    self.int_to_state_map[msg.sender_id] = StateHandler.modified()
                    self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", self.CACHE_CONFIG.block_size)
                    self.cpu_stats[self.CPU_NUMS].increment("invalidation")


                    return self.CACHE_CONFIG.block_size // 2
            else: #READ_REQ
                if cnt == 0:
                    self.int_to_state_map[msg.sender_id] = StateHandler.exclusive()
                elif cnt == 1:
                    # Transition from Modified to Shared
                    for i in range(self.CPU_NUMS):
                        if flags[i] and caches[i]:
                            cnt-=1
                            if has_modified:
                                assert caches[i].state == StateHandler.modified()
                                caches[i].dirty = False  # Reset the dirty bit if Modified
                            caches[i].state = StateHandler.shared()
                    assert cnt == 0
                    self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                    self.cpu_stats[self.CPU_NUMS].add_many('data_traffic', self.CACHE_CONFIG.block_size)
                    if has_modified:
                        return max(self.CACHE_CONFIG.block_size // 2, self.TIME_CONFIG.write_back_mem)
                    else:
                        return self.CACHE_CONFIG.block_size // 2
                else:
                    assert not has_modified
                    # All other caches must also transition to Shared
                    for i in range(self.CPU_NUMS):
                        if flags[i] and caches[i]:
                            cnt-=1
                            assert caches[i].state == StateHandler.shared()

                    assert cnt == 0
                    self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                    self.cpu_stats[self.CPU_NUMS].add_many('data_traffic', self.CACHE_CONFIG.block_size)
                    return self.CACHE_CONFIG.block_size // 2


        else:
            assert flags[msg.sender_id]
            assert  msg.message_type == MessageType.WRITE_REQ
            if cnt == 1:
                # Exclusive or Shared to Modified directly
                assert caches[msg.sender_id].state == StateHandler.exclusive() or caches[msg.sender_id].state == StateHandler.shared()
                caches[msg.sender_id].state = StateHandler.modified()
            else:
                # Invalidate others if Shared to Modified
                assert caches[msg.sender_id].state == StateHandler.shared()
                caches[msg.sender_id].state = StateHandler.modified()
                for i in range(self.CPU_NUMS):
                    if i != msg.sender_id and flags[i] and caches[i]:
                        assert caches[i].state == StateHandler.shared()
                        caches[i].state=StateHandler.invalid()
                        caches[i].valid=False
                self.cpu_stats[self.CPU_NUMS].increment('invalidation')
            return 0
        return self.TIME_CONFIG.write_back_mem  # No additional delay