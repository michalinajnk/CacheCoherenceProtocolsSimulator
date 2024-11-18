import math
from dataclasses import dataclass

@dataclass(eq=True, frozen=True)
class CacheAddress:
    tag: int
    set_index: int

