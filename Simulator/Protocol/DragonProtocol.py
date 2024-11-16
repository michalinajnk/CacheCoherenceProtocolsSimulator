from Simulator.Cache.MessageType import MessageType
from Simulator.Protocol.CacheProtocol import CacheProtocol
from Simulator.StateMachine.StateHandler import StateHandler


class DragonProtocol(CacheProtocol):
    """
    Dragon Cache Coherence Protocol implementation.
    Handles specific logic for the Dragon protocol for cache coherence.
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
        return 1  # Identifier for Dragon protocol

    def process_msg(self, msg, flags, caches):
        """
        Process a message in the context of the Dragon cache coherence protocol.
        Handles transitions between cache states and simulates bus interactions.
        """
        cnt = sum(flags)  # Count how many caches hold a copy

        # Check if any cache is in the Modified or SharedModified state
        has_modified = any(
            flags[i] and caches[i].get_state() == StateHandler.modified()
            for i in range(self.CPU_NUMS)
        )
        has_shared_modified = any(
            flags[i] and caches[i].get_state() == StateHandler.owned()
            for i in range(self.CPU_NUMS)
        )

        if not flags[msg.sender_id]:  # Start from Invalid State
            if msg.message_type == MessageType.WRITE_REQ:
                if cnt == 0:
                    self.int_to_state_map[msg.sender_id] = StateHandler.modified()
                else:
                    for i in range(self.CPU_NUMS):
                        if flags[i]:
                            if has_modified or has_shared_modified:
                                assert (
                                    caches[i].get_state() == StateHandler.modified()
                                    or caches[i].get_state()
                                    == StateHandler.owned()
                                )
                                caches[i].set_dirty(False)  # Transition to SharedClean
                            caches[i].set_state(StateHandler.shared())
                    self.int_to_state_map[
                        msg.sender_id
                    ] = StateHandler.owned()
                    self.cpu_stats[self.CPU_NUMS]["update"] += 1
                    self.cpu_stats[self.CPU_NUMS]["data_traffic"] += (
                        self.CACHE_CONFIG.block_size + 4 * cnt
                    )
                    return self.CACHE_CONFIG.block_size // 2 + self.TIME_CONFIG.bus_update
            else:  # READ_REQ
                if cnt == 0:
                    self.int_to_state_map[msg.sender_id] = StateHandler.exclusive()
                elif cnt == 1:
                    if has_modified:
                        for i in range(self.CPU_NUMS):
                            if (
                                flags[i]
                                and caches[i].get_state()
                                == StateHandler.modified()
                            ):
                                caches[i].set_state(StateHandler.shared())
                        self.int_to_state_map[
                            msg.sender_id
                        ] = StateHandler.shared()
                        self.cpu_stats[self.CPU_NUMS]["data_traffic"] += self.CACHE_CONFIG.block_size
                        return self.CACHE_CONFIG.block_size // 2
                    elif has_shared_modified:
                        self.int_to_state_map[
                            msg.sender_id
                        ] = StateHandler.shared()
                        self.cpu_stats[self.CPU_NUMS]["data_traffic"] += self.CACHE_CONFIG.block_size
                        return self.CACHE_CONFIG.block_size // 2
                    else:
                        for i in range(self.CPU_NUMS):
                            if flags[i]:
                                caches[i].set_state(StateHandler.shared())
                        self.int_to_state_map[
                            msg.sender_id
                        ] = StateHandler.shared().get_instance()
                        self.cpu_stats[self.CPU_NUMS]["data_traffic"] += self.CACHE_CONFIG.block_size
                        return self.CACHE_CONFIG.block_size // 2
                else:
                    for i in range(self.CPU_NUMS):
                        if flags[i]:
                            caches[i].set_state(StateHandler.shared())
                    self.int_to_state_map[
                        msg.sender_id
                    ] = StateHandler.shared().get_instance()
                    self.cpu_stats[self.CPU_NUMS]["data_traffic"] += self.CACHE_CONFIG.block_size
                    return self.CACHE_CONFIG.block_size // 2
        else:  # Flags[msg.sender_id] is True
            assert msg.type == MessageType.WRITE_REQ
            if caches[msg.sender_id].get_state() == StateHandler.exclusive():
                caches[msg.sender_id].set_state(StateHandler.modified())
            elif caches[msg.sender_id].get_state() == StateHandler.shared():
                if cnt == 1:
                    caches[msg.sender_id].set_state(StateHandler.modified())
                else:
                    for i in range(self.CPU_NUMS):
                        if i != msg.sender_id and flags[i]:
                            caches[i].set_state(StateHandler.shared())
                    caches[msg.sender_id].set_state(StateHandler.owned())
                    self.cpu_stats[self.CPU_NUMS]["update"] += 1
                    self.cpu_stats[self.CPU_NUMS]["data_traffic"] += 4 * (cnt - 1)
                    return self.TIME_CONFIG.bus_update
            elif caches[msg.sender_id].get_state() == StateHandler.owned():
                if cnt == 1:
                    caches[msg.sender_id].set_state(StateHandler.modified())
                else:
                    for i in range(self.CPU_NUMS):
                        if i != msg.sender_id and flags[i]:
                            caches[i].set_state(StateHandler.shared())
                    self.cpu_stats[self.CPU_NUMS]["update"] += 1
                    self.cpu_stats[self.CPU_NUMS]["data_traffic"] += 4 * (cnt - 1)
                    return self.TIME_CONFIG.bus_update

        return self.TIME_CONFIG.load_block_from_mem
