from .CacheConfig import CacheConfig
from .TimeConfig import TimeConfig


class Config:
    def __init__(self, cpu_nums):
        self.CPU_NUMS = cpu_nums
        self.TIME_CONFIG = None
        self.CACHE_CONFIG = None
        self.protocol = None
        self.instructions = set()
        self.CPU_STATS = []
        self.size_of_word = 4  # each word is 4 byte



    def words_per_block(self):
        return self.CACHE_CONFIG.block_size / self.size_of_word

    def setProtocl(self, protocol):
        self.protocol = protocol


    def setTimeConfig(self, CACHE_HIT, LOAD_BLOCK_FR0M_MEM, WRITE_BACK_MEM, BUS_UPDATE):
        self.TIME_CONFIG = TimeConfig(CACHE_HIT,LOAD_BLOCK_FR0M_MEM, WRITE_BACK_MEM, BUS_UPDATE)


    def setCacheConfig(self, CACHE_SIZE, ASSOCIATIVITY, BLOCK_SIZE):
        self.CACHE_CONFIG = CacheConfig(CACHE_SIZE, ASSOCIATIVITY, BLOCK_SIZE)



