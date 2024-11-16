from collections import deque
from Simulator.Cache.CacheLine import CacheLine
from Simulator.StateMachine.StateHandler import StateHandler


class CacheSet:
    """Manages a set of CacheLine objects, handling insertion, eviction, and state management based on LRU
    and interacting directly with the cache lines according to the cache coherence protocol."""

    def __init__(self, config, associativity, identifier):
        self.associativity = associativity
        self.identifier = identifier
        self.lines = [CacheLine() for _ in range(associativity)]
        self.lru_queue = deque(range(associativity))  # Track LRU by index
        self.tag_to_index = {}  # Maps tags to indices for quick lookup
        self.config = config

    def is_hit(self, tag, modify=False):
        hit = False
        for line in self.lines:
            if line.valid and line.tag == tag:
                if modify:
                    line.set_dirty(True)
                return True
        return hit

    def is_hit_readonly(self, tag, modify=False):
        for idx, line in enumerate(self.lines):
            if line.valid and line.tag == tag:
                self.config.CPU_STATS[idx].increment("cache_hit")
                if (line.state == StateHandler.modified()
                        or line.state == StateHandler.exclusive()):
                    self.config.CPU_STATS[self.config.CPU_NUMS].increment("private")
                else:
                    self.config.CPU_STATS[self.config.CPU_NUMS].increment("public")
            if self.config.protocol.get_protocol() < 1:
                if modify and line.dirty == False:
                    return False
            elif modify:
                return False
            return True
        return False


    def access_line(self, tag, modify=False):
        """Access a line with the given tag, potentially modifying it if 'modify' is True."""
        index = self.tag_to_index.get(tag)
        if index is not None and self.lines[index].is_valid and self.lines[index].tag == tag:
            self.lru_queue.remove(index)
            self.lru_queue.appendleft(index)
            if modify:
                self.lines[index].set_dirty(True)
            return self.lines[index]
        return None

    def is_full(self):
        """Check if all cache lines are valid."""
        return all(line.is_valid for line in self.lines)

    def add_or_replace_line(self, tag, is_write):
        """Add a new line with the given tag, or replace the least recently used one if the set is full."""
        if len(self.lru_queue) < self.associativity:
            # There is space to add a new line
            index = self.lru_queue.pop()  # Use an existing index that is considered least recently used
            new_line = self.lines[index]
            new_line.tag = tag
            new_line.valid = True
            new_line.dirty = is_write
            self.lru_queue.appendleft(index)
            self.tag_to_index[tag] = index
            return new_line, False  # No eviction happened
        else:
            # Replace the least recently used line
            lru_index = self.lru_queue.pop()
            evicted_line = self.lines[lru_index]
            was_dirty = evicted_line.dirty and evicted_line.valid
            old_tag = evicted_line.tag
            if old_tag in self.tag_to_index:
                del self.tag_to_index[old_tag]  # Remove old tag
            evicted_line.update(tag, is_write)
            self.lru_queue.appendleft(lru_index)
            self.tag_to_index[tag] = lru_index
            return evicted_line, was_dirty


    def need_write_back(self, tag):
        """
        Determines if the least recently used line needs to be written back to memory.
        Args:
            tag (int): The tag being inserted, used to avoid write-back if it matches the LRU tag.
        Returns:
            bool: True if the least recently used line is dirty, valid, and its tag does not match the incoming tag.
        """
        if self.is_full():
            lru_index = self.lru_queue[-1]
            lru_line = self.lines[lru_index]
            return lru_line.dirty and lru_line.valid and lru_line.tag != tag
        return False


    def load_line(self, tag, is_write):
        """Load a line with the specified tag into the cache, handling eviction if necessary."""
        line, was_dirty = self.add_or_replace_line(tag, is_write)
        cycles = self.config.TIME_CONFIG.load_block_from_mem
        if was_dirty:
            cycles += self.config.TIME_CONFIG.write_back_mem
        return cycles

    def get_state(self, index):
        """Get the state of the line at the specified index."""
        return self.lines[index].state if index < len(self.lines) and self.lines[index].is_valid else None

    def set_state(self, index, state):
        """Set the state of the line at the specified index."""
        if index < len(self.lines):
            self.lines[index].state = state
