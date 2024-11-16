"""
This class will mimic the behavior of a cache line,
 holding data, a tag, a validity bit, a dirty bit, and  a state for cache protocols
"""


class CacheLine:
    def __init__(self):
        self.valid = False
        self.tag = 0
        self.dirty = False
        self.data = None
        self.state = None  #  state for coherence protocol

    def set_state(self, new_state):
        self.state = new_state

    def is_valid(self):
        return self.valid

    def set_valid(self, new_state):
        self.valid = new_state

    def set_dirty(self, dirty):
        self.dirty = dirty


    def update(self, tag, dirty):
        self.valid = True
        self.tag = tag
        self.dirty = dirty