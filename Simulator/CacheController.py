from Cache import Cache
from abc import ABC, abstractmethod


class CacheController(ABC):

    def __init__(self, size, associativity, block_size, core):
        self.cache = Cache(size, associativity, block_size)
        self.hit = 0
        self.miss = 0
        self.privAccess = 0
        self.pubAccess = 0
        self.core = core
        self.can_provide_flag = False
        self.unstall_address = -1
        self.unstall_action = ""
        self.stalled = False
        

    def stall(self):
        self.stalled = True
        self.core.stall()
        
    def unstall(self, shared):
        pass
        
    def can_provide(self):
        result = self.can_provide_flag
        self.can_provide_flag = False
        return result

    def connect_bus(self, bus):
        self.bus = bus

    def get_cache(self):
        return self.cache

    def get_core_identifier(self):
        return self.core.get_identifier()

    def get_miss_rate(self):
        try:
            return 100 * self.miss / (self.hit+self.miss)
        except ZeroDivisionError:
            return "divide by zero"

    def get_hit(self):
        return self.hit

    def get_miss(self):
        return self.miss

    def get_priv_rate(self):
        try:
            return 100 * self.privAccess / (self.pubAccess + self.privAccess)
        except ZeroDivisionError:
            return "divide by zero"

    def get_pub_rate(self):
        try:
            return 100 * self.pubAccess / (self.pubAccess + self.privAccess)
        except ZeroDivisionError:
            return "divide by zero"

    def busRd(self, address):
        self.core.stall()
        self.unstall_address = address
        self.unstall_action = Constants.UnstallAction.PrRd
        self.bus.add_transaction(Transaction(Constants.TransactionTypes.BusRd, self.core, address))

    def busRdX(self, address):
        self.core.stall()
        self.unstall_address = address
        self.unstall_action = Constants.UnstallAction.PrWr
        self.bus.add_transaction(Transaction(Constants.TransactionTypes.BusRdX, self.core, address))

    def busUpd(self, address):
        self.core.stall()
        self.unstall_address = address
        self.unstall_action = Constants.UnstallAction.BusUpd
        self.bus.add_transaction(Transaction(Constants.TransactionTypes.BusUpd, self.core, address))
    @abstractmethod
    def prRd(self, address):
        pass

    @abstractmethod
    def prWr(self, address):
        pass

    # returns true if data is to be copied, false if data is not to be copied
    @abstractmethod
    def snoop(self, transaction):
        pass