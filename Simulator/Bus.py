class Transection:
    def __init__(self, address, size, type):
        self.address = address
        self.size = size
        self.type = type

    def get_address(self):
        return self.address

    def get_size(self):
        return self.size

    def get_type(self):
        return self.type

    def __str__(self):
        return "Address: " + str(self.address) + " Size: " + str(self.size) + " Type: " + self.type

class Bus:
    def __init__(self):
        # initialize the bus
        self.data_traffic = 0  # total data traffic on the bus
        self.transactions = 0  # total transactions on the bus
        self.invalidation_count = 0  # invalidation requests
        self.update_count = 0  # update operations

    def send_data(self, size_in_bytes):
        self.data_traffic += size_in_bytes
        self.transactions += 1  # each data transfer is a transaction

    def send_invalidation(self):
        self.invalidation_count += 1
        self.transactions += 1  # invalidation is also a transaction

    def send_update(self, size_in_bytes):
        self.update_count += 1
        self.send_data(size_in_bytes)  # update is a data transfer

    def get_data_traffic(self):
        return self.data_traffic

    def get_transaction_count(self):
        return self.transactions

    def get_invalidation_count(self):
        return self.invalidation_count
    
    def print_stats(self):
        print(f"Total data traffic: {self.data_traffic} bytes")
        print(f"Total transactions: {self.transactions}")
        print(f"Invalidation requests: {self.invalidation_count}")
        print(f"Update operations: {self.update_count}")
        return None