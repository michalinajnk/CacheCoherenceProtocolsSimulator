from collections import deque

from Simulator.Cache.CacheLine import CacheLine


class CacheSet:
    """Manages a set of CacheLine objects, handling insertion and eviction based on LRU
    and interacting directly with the cache lines."""

    def __init__(self, associativity, identifier):
        """
        Initializes a CacheSet with a specified number of lines (associativity) and a unique identifier.
        """
        self.associativity = associativity
        self.identifier = identifier
        self.lines = [CacheLine() for _ in range(associativity)]
        self.lru_queue = deque()
        self.tag_to_index = {}  # Maps tags to indices for quick lookup

    def find_line(self, tag):
        """
        Finds and returns the cache line with the given tag, updating its position in the LRU queue if found.
        """
        index = self.tag_to_index.get(tag)
        if index is not None and self.lines[index].is_valid and self.lines[index].cache_tag == tag:
            self.lru_queue.remove(index)
            self.lru_queue.appendleft(index)
            return self.lines[index]
        return None

    def replace_line(self, tag, dirty):
        """
        Replaces the least recently used cache line with a new line with the specified tag and dirty flag.
        """
        if not self.lru_queue:
            # Should never happen if associativity > 0
            raise RuntimeError("No available lines to replace in CacheSet")

        lru_index = self.lru_queue.pop()
        old_line = self.lines[lru_index]
        if old_line.is_valid:
            self.tag_to_index.pop(old_line.cache_tag, None)

        old_line.update(tag, dirty)
        self.lru_queue.appendleft(lru_index)
        self.tag_to_index[tag] = lru_index
        return old_line
