class Statistics:
    def __init__(self):
        self.data = {}

    def increment(self, key, value=1):
        if key in self.data:
            self.data[key] += value
        else:
            self.data[key] = value

    def get_stat(self, key):
        return self.data.get(key, 0)