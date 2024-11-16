class CacheAddress:
    def __init__(self, tag, set_index):
        self.tag = tag
        self.set_index = set_index

    def __eq__(self, other):
        if isinstance(other, CacheAddress):
            return self.tag == other.tag and self.set_index == other.set_index
        return False

    def __hash__(self):
        # Start with a prime number and multiply + add for each relevant field
        hash_value = 17
        hash_value = hash_value * 31 + hash(self.tag)
        hash_value = hash_value * 31 + hash(self.set_index)
        return hash_value