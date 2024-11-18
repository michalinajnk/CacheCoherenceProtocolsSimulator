import threading
from collections import deque
from Simulator.Cache.CacheLine import CacheLine
from Simulator.StateMachine.StateHandler import StateHandler
import logging
MESI_PROTOCOL = 0

class CacheSet:
    """Manages a set of CacheLine objects, handling insertion, eviction, and state management based on LRU
    and interacting directly with the cache lines according to the cache coherence protocol."""

    def __init__(self, config, associativity, identifier):
        self.associativity = associativity
        self.identifier = identifier
        self.config = config
        self.lock = threading.Lock()
        self.lines = [CacheLine() for _ in range(associativity)]
        self.lru_queue = deque(range(associativity))
        for line in self.lines:
            line.state = StateHandler.invalid()
        logging.debug(f"CacheSet initialized with ID={identifier}, associativity={associativity}")

    def is_full(self):
        """Checks if all lines in the cache set are valid, indicating full capacity."""
        return all(line.valid for line in self.lines)

    def find_line_index(self, tag):
        """Finds the index of a line with a specific tag, returns None if not found."""
        for index, line in enumerate(self.lines):
            if line.valid and line.tag == tag:
                return index
        return None

    def is_hit(self, tag, isWrite=False):
        """Checks for a cache hit, and optionally modifies the line's state."""
        with self.lock:
            line_index = self.find_line_index(tag)
            if line_index is not None:
                line = self.lines[line_index]
                self.lru_queue.remove(line_index)
                self.lru_queue.appendleft(line_index)
                logging.info(f"Cache hit: tag={tag}, modify={isWrite}")
                if isWrite:
                    line.dirty = True
                return True
            logging.info(f"Cache miss: tag={tag}")
            return False

    def is_hit_msg(self, tag):
        """Check for a hit and return the line without affecting LRU order."""
        with self.lock:
            for line in self.lines:
                if line.valid and line.tag == tag:
                    return line
            return None

    def is_hit_readonly(self, tag, isWrite=False):
        """Check for a hit without modifying any state, used for const operations."""
        with self.lock:
            for line in self.lines:
                if line.valid and line.tag == tag:
                    self.config.CPU_STATS[self.identifier].increment("cache_hit")
                    if line.state == StateHandler.modified() or line.state == StateHandler.exclusive():
                        self.config.CPU_STATS[self.config.CPU_NUMS].increment("private")
                    else:
                        self.config.CPU_STATS[self.config.CPU_NUMS].increment("public")
                    if self.config.protocol.get_protocol() == MESI_PROTOCOL:
                        if isWrite and not line.dirty:
                            return False  # Cannot write if line is not already dirty
                    elif isWrite:
                        return False
                    return True
            return False


    def add_or_replace_line(self, tag, is_write):
        """Adds a new line or replaces the least recently used line with new content."""
        with self.lock:
            # Always evict or reuse the least recently used line (popped from the end of the LRU queue)
            lru_index = self.lru_queue.pop()  # Remove the least recently used line

            evicted_line = self.lines[lru_index]
            evicted_line.tag = tag
            evicted_line.valid = True
            evicted_line.dirty = is_write
            evicted_line.state=StateHandler.invalid()  # Reset state to invalid, coherence protocol will update

            # Update this line to be the most recently used
            self.lru_queue.appendleft(lru_index)
            logging.info(f"Cache line updated at index {lru_index}: tag={tag}, write={is_write}")

            return evicted_line


    def load_line(self, tag, isWrite):
        with self.lock:
            # Check the state constraints based on the protocol
            for line in self.lines:
                if line.valid and line.tag == tag:
                    if isWrite:
                        assert line.state in [self.config.protocol.intToStringMap[self.identifier].modified()]
                    if line.state == self.config.protocol.intToStringMap[self.identifier].shared():
                        assert not isWrite

            if not self.is_full():
                # Find an invalid line to use
                for i, line in enumerate(self.lines):
                    if not line.valid:
                        line.is_valid = True
                        line.tag = tag
                        line.dirty = isWrite
                        line.state = self.config.protocol.intToStringMap[self.identifier].invalid()
                        self.lru_queue.remove(i)
                        self.lru_queue.appendleft(i)
                        return self.config.TIME_CONFIG.load_block_from_mem
            else:
                # Evict the least recently used line
                lru_index = self.lru_queue.pop()
                evicted_line = self.lines[lru_index]
                write_back_cycles = self.config.TIME_CONFIG.write_back_mem if evicted_line.dirty else 0
                evicted_line.tag = tag
                evicted_line.dirty = isWrite
                evicted_line.state = self.config.protocol.intToStringMap[self.identifier].invalid()  # Assume invalid, set later
                self.lru_queue.appendleft(lru_index)
                return self.config.TIME_CONFIG.load_block_from_mem + write_back_cycles

            return 0

    def need_write_back(self, tag):
        """Determines if the least recently used line needs to be written back before eviction."""
        with self.lock:
            if self.is_full():
                lru_index = self.lru_queue[-1]  # Peek at the least recently used without removing it
                lru_line = self.lines[lru_index]
                return lru_line.dirty and lru_line.valid and lru_line.tag != tag
            return False
