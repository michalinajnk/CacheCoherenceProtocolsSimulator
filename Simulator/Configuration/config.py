from psutil import cpu_times
from sympy.physics.vector import Vector

from Simulator.Configuration.CacheConfig import CacheConfig
from Simulator.Configuration.TimeConfig import TimeConfig


class Config:
    def __init__(self, cpu_nums):
        self.CPU_NUMS = cpu_nums
        self.TIME_CONFIG = None
        self.CACHE_CONFIG = None
        self.protocol = None
        self.insts = set()
        self.CPU_STATS = []

    def setProtocl(self, protocol):
        self.protocol = protocol




    def setTimeConfig(self, CACHE_HIT,LOAD_BLOCK_FR0M_MEM, WRITE_BACK_MEM, BUS_UPDATE):
        self.TIME_CONFIG = TimeConfig(CACHE_HIT,LOAD_BLOCK_FR0M_MEM, WRITE_BACK_MEM, BUS_UPDATE)


    def setCacheConfig(self, CACHE_SIZE, ASSOCIATIVITY,BLOCK_SIZE):
        self.CACHE_CONFIG = CacheConfig(CACHE_SIZE, ASSOCIATIVITY, BLOCK_SIZE)



