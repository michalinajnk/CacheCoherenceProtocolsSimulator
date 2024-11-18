import math
from dataclasses import dataclass

@dataclass(eq=True, frozen=True)
class CacheAddress:
    tag: int
    set_index: int

    def to_physical_address(self, block_size: int) -> int:
        block_offset_bits = int(math.log2(block_size))
        set_index_bits = int(math.log2(self.set_index + 1))
        return (self.tag << (block_offset_bits + set_index_bits)) | (self.set_index << block_offset_bits)
