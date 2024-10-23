from Bus import *
class CacheBlock:
    def __init__(self):
        self.valid = False       # is the block valid?
        self.tag = None          # tag bits
        self.dirty = False       # is the block dirty?
        self.data = None         # block data

class Cache:
    def __init__(self, cache_size, block_size, associativity, bus):
        # initialize cache parameters
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.num_sets = cache_size // (block_size * associativity)  # set number of cache
        self.BUS = bus

        # initialize cache blocks, each block has a valid bit, tag bits, dirty bit, and data
        self.cache = [[CacheBlock() for _ in range(associativity)] for _ in range(self.num_sets)]
        self.lru_counters = [[0 for _ in range(associativity)] for _ in range(self.num_sets)] # LRU counter
        
        # counters
        self.hitCount = 0
        self.missCount = 0
        
    def print_stats(self):
        """
        Prints the statistics of the cache.
        Returns:
            None
        """
        print(f"Number of hits: {self.hitCount}")
        print(f"Number of misses: {self.missCount}")
        return None

    def access(self, address, is_write) -> (int):
        """
        Accesses the cache with the given address and determines if it is a hit or miss.

        Args:
            address (int): The memory address to access.
            is_write (bool): Flag indicating if the access is a write operation.

        Returns:
            int: The number of cycles needed for the access. Returns 1 if it is a hit, 
             and 100 if it is a miss.
        """
        # change the address from hex to int
        address = int(address, 16)
        
        block_offset = address % self.block_size
        index = (address // self.block_size) % self.num_sets
        tag = address // (self.block_size * self.num_sets)

        # check if the block is in the cache
        for i, block in enumerate(self.cache[index]):
            if block.valid and block.tag == tag:
                # hit
                self.update_lru(index, i)
                if is_write:
                    block.dirty = True  # if is write operation, set the block as dirty
                self.hitCount += 1
                return 0  # hit, 0 extra stall cycles needed
        # miss
        self.replace_block(index, tag, is_write)
        self.missCount += 1
        # need to fetch data from memory, make 
        return 99  # miss, 99 extra cycles needed to fetch data from memory

    def update_lru(self, index, accessed_block):
        
        for i in range(self.associativity):
            if i != accessed_block:
                self.lru_counters[index][i] += 1  # if not accessed block, increment the counter
        self.lru_counters[index][accessed_block] = 0  # if accessed block, reset the counter

    def replace_block(self, index, tag, is_write):
        # find the least recently used block address and replace it
        lru_block_index = self.lru_counters[index].index(max(self.lru_counters[index]))
        block_to_replace = self.cache[index][lru_block_index]

        # if the block is dirty, write back to memory
        if block_to_replace.dirty:
            self.write_back_to_memory(block_to_replace)

        # replace the block
        block_to_replace.valid = True
        block_to_replace.tag = tag
        block_to_replace.dirty = is_write
        block_to_replace.data = None  # fetch data from memory

        # update LRU counters
        self.update_lru(index, lru_block_index)

    def write_back_to_memory(self, block):
        # make transaction to write back to memory
        transaction = Transection(block.tag, self.block_size, "write")
        self.BUS.send_data(transaction.get_size())
        return 100  # 100 cycles needed to write back to memory