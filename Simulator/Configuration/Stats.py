class Statistics:
    def __init__(self):
        self.counters = {}

    def increment(self, key):
        if key in self.counters:
            self.counters[key] += 1
        else:
            self.counters[key] = 1

    def add_many(self, key, val):
        if key in self.counters:
            self.counters[key] += val
        else:
            self.counters[key] = val

    def get_count(self, key):
        return self.counters.get(key, 0)

    def set_count(self, key, val):
        self.counters[key] = val

