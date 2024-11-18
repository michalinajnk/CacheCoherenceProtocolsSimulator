class CacheLine:
    def __init__(self, tag=0, valid=False, dirty=False, state=None):
        self._valid = valid
        self._tag = tag
        self._dirty = dirty
        self._state = state

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, value):
        self._valid = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        self._dirty = value
        
    def set_dirty(self, value):
        self._dirty = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state

    def update(self, tag, is_write):
        """Updates the cache line with new tag and sets the line as valid and potentially dirty."""
        self.tag = tag
        self.valid = True
        self.dirty = is_write

    def clear(self):
        """Resets the cache line to invalid and clean."""
        self.valid = False
        self.dirty = False
        self.tag = 0
        self.state = None

    def __str__(self):
        """Provides a simple string representation of the cache line."""
        return f"Tag: {self.tag}, Valid: {self.valid}, Dirty: {self.dirty}, State: {self.state}"
    
    def get_state(self):
        return self._state
    
