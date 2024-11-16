class TimeConfig:
    def __init__(self, cache_hit=10, load_block_from_mem=100, write_back_mem=150, bus_update=50):
        self.cache_hit = cache_hit
        self.load_block_from_mem = load_block_from_mem
        self.write_back_mem = write_back_mem
        self.bus_update = bus_update

    def display_times(self):
        print("Cache Hit Time:", self.cache_hit)
        print("Load Block from Memory Time:", self.load_block_from_mem)
        print("Write Back to Memory Time:", self.write_back_mem)
        print("Bus Update Time:", self.bus_update)


