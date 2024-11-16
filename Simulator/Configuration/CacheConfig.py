class CacheConfig:
    def __init__(self,cache_size, assoc,  blok_s):
        self.cache_size = cache_size
        self.associativity = assoc
        self.block_size = blok_s