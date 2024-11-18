from Simulator.Cache.MessageType import MessageType
from Simulator.Protocol.CacheProtocol import CacheProtocol
from Simulator.StateMachine.StateHandler import StateHandler
import logging

class DragonProtocol(CacheProtocol):
    def __init__(self, config):
        super().__init__()
        self.cpu_stats = config.CPU_STATS
        self.CPU_NUMS = config.CPU_NUMS
        self.CACHE_CONFIG = config.CACHE_CONFIG
        self.TIME_CONFIG = config.TIME_CONFIG

    def get_protocol(self):
        return 2  # Ensuring protocol identification matches with C++

    def process_msg(self, msg, flags, caches):
        cnt = sum(flags)
        has_modified = any(
            flags[i] and caches[i] is not None and caches[i].get_state() == StateHandler.modified() for i in
            range(self.CPU_NUMS))
        has_shared_modified = any(
            flags[i] and caches[i] is not None and caches[i].get_state() == StateHandler.owned() for i in
            range(self.CPU_NUMS))

        if not flags[msg.sender_id]:
            # Handling for invalid or uninitialized cache at sender_id
            if msg.message_type == MessageType.WRITE_REQ:
                if cnt == 0:
                    # No caches hold a copy, so set sender to modified directly if possible
                    if caches[msg.sender_id]:
                        self.int_to_state_map[msg.sender_id] = StateHandler.modified()
                elif cnt == 1:
                    self.update_for_write(has_modified, has_shared_modified, flags, caches, msg)
                else:
                    self.set_all_to_shared_clean(flags, caches, msg, cnt)
                    return self.CACHE_CONFIG.block_size / 2 + self.TIME_CONFIG.bus_update
            else: #READ
                if cnt == 0:
                    self.int_to_state_map[msg.sender_id]  = StateHandler.exclusive()
                elif cnt == 1:
                    if has_modified: #MOdified
                        for i in range(self.CPU_NUMS):
                            if flags[i] and caches[i] is not None and caches[i].get_state() == StateHandler.modified():
                                caches[i].state = StateHandler.modified()
                                assert caches[i].dirty == True
                        self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                        self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", self.CACHE_CONFIG.block_size)
                        return self.CACHE_CONFIG.block_size / 2
                    elif has_shared_modified: #o
                        self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                        self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", self.CACHE_CONFIG.block_size)
                    else: # E,S
                        for i in range(self.CPU_NUMS):
                            if flags[i]:
                                cnt -=  1
                                assert (caches[i].get_state() == StateHandler.exclusive()
                                        or caches[i].get_state() == StateHandler.shared())
                                caches[i].state = StateHandler.shared()
                                assert caches[i].dirty == False
                        assert cnt == 0
                        self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                        self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", self.CACHE_CONFIG.block_size)
                        return self.CACHE_CONFIG.block_size / 2
                else: #shared or shared+ow
                    assert has_modified == False
                    for i in range(self.CPU_NUMS):
                        if flags[i]:
                            cnt -= 1
                            assert (caches[i].get_state() == StateHandler.shared() or
                                    caches[i].get_state() == StateHandler.owned())
                            if caches[i].get_state() == StateHandler.shared():
                                assert caches[i].dirty == False
                    assert cnt == 0
                    self.int_to_state_map[msg.sender_id] = StateHandler.shared()
                    self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", self.CACHE_CONFIG.block_size)
                    return self.CACHE_CONFIG.block_size / 2
        else:
            assert flags[msg.sender_id]
            assert msg.message_type == MessageType.WRITE_REQ
            if caches[msg.sender_id].get_state() == StateHandler.exclusive():
                # Exclusive to Modified, PrWr/-
                assert cnt == 1
                caches[msg.sender_id].state = StateHandler.modified()
            elif caches[msg.sender_id].get_state() == StateHandler.shared():
                if cnt == 1:  # no need to update, transfer to DragonModified
                    assert not caches[msg.sender_id].dirty
                    caches[msg.sender_id].state = StateHandler.modified()
                else:  # SharedClean to SharedModified, others need to be updated and transfer to SharedClean
                    for i in range(self.CPU_NUMS):
                        if i != msg.sender_id and flags[i]:
                            assert caches[i].get_state() in [StateHandler.shared(),
                                                             StateHandler.owned()]
                            if caches[i].get_state() == StateHandler.owned():
                                assert has_shared_modified and caches[i].dirty
                                caches[i].dirty = False  # to shared clean
                                caches[i].state = StateHandler.shared()
                            else:
                                assert not caches[i].dirty
                    caches[msg.sender_id].state = StateHandler.owned()
                    assert not caches[msg.sender_id].dirty
                    self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", 4 * (cnt - 1))
                    self.cpu_stats[self.CPU_NUMS].increment("update")
                    return self.TIME_CONFIG.bus_update

            elif caches[msg.sender_id].get_state() == StateHandler.owned():
                if cnt == 1:
                    assert caches[msg.sender_id].dirty
                    caches[msg.sender_id].state = StateHandler.modified()
                else:  # other copies are all in SharedClean state
                    for i in range(self.CPU_NUMS):
                        if i != msg.sender_id and flags[i]:
                            assert caches[i].get_state() == StateHandler.shared()
                            assert not caches[i].dirty
                    self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", 4 * (cnt - 1))
                    self.cpu_stats[self.CPU_NUMS].increment("update")
                    return self.TIME_CONFIG.bus_update

            elif caches[msg.sender_id].get_state() == StateHandler.modified():
                # do nothing, fall through
                pass
            else:
                print("msg.sender_id", msg.sender_id)
                print("caches[msg.sender_id].get_state()", caches[msg.sender_id].get_state())
                print("msg.message_type", msg.message_type)
                print("cnt", cnt)
                assert False  # never reach here
            return 0
        return self.TIME_CONFIG.load_block_from_mem


    def update_for_write(self, has_modified, has_shared_modified, flags, caches, msg):
        for i in range(self.CPU_NUMS):
            if flags[i]:
                if has_modified or has_shared_modified:
                    caches[i].set_dirty(False)
                caches[i].set_state(StateHandler.shared())
        self.int_to_state_map[msg.sender_id] = StateHandler.modified()
        self.cpu_stats["updates"] += 1
        self.cpu_stats["data_traffic"] += self.CACHE_CONFIG.block_size + 4


    def set_all_to_shared_clean(self, flags, caches,  msg,  cnt):
        for i in range(self.CPU_NUMS):
            if flags[i]:
                assert caches[i].get_state() == StateHandler.shared() or caches[i].get_state() == StateHandler.owned()
                if caches[i].get_state() == StateHandler.shared():
                    assert caches[i].dirty == False
                caches[i].state = StateHandler.shared()
                if caches[i].get_state() == StateHandler.owned():
                    assert caches[i].dirty == True
                    caches[i].dirty = False
                assert caches[i].dirty == False
        self.int_to_state_map[msg.sender_id]  = StateHandler.owned()
        self.cpu_stats[self.CPU_NUMS].increment("update")
        self.cpu_stats[self.CPU_NUMS].add_many("data_traffic", self.CACHE_CONFIG.block_size + 4 * cnt)


