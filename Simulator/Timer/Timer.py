from typing import List
import sys

class Timerr:
    def __init__(self):
        # self.ticks = sys.maxsize
        self.ticks = 0
        self.observers = []  #observers of timer ticks
        self.bus = None
        self.active_count = 0

    def attach(self, observer):
        """
        Attach an observer to the timer.

        Args:
            observer: An instance of a class implementing the Observer interface.
        """
        self.observers.append(observer)

    def tick(self):
        """
        Increment the timer and notify all observers.

        Returns:
            done (bool): True if all observers are not active, False otherwise.
        """
        self.ticks += 1
        return self.notify(self.ticks)

    def notify(self, now):
        """
        Notify all observers about the current time tick.

        Args:
            now (int): Current time tick.

        Returns:
            done (bool): True if all observers are not active, False otherwise.
        """
        self.active_count = 0
        for observer in self.observers:
            still_processing = observer.update(now)
            # print(observer,"still_processing",still_processing)
            if still_processing:
                # print(observer,"still_processing",still_processing, observer.current_instruction)
                # print(observer.halt_cycles)
                self.active_count += 1

        # Propagate bus requests and replies
        if self.bus:
            self.bus.propagate_requests()
            self.bus.propagate_replies()

        # Return True if all observers are active
        print(f"current time is {now}, active_count is {self.active_count}")
        # print(active_count == 0)
        # return active_count != len(self.observers)
        return self.active_count == 0

    def set_bus(self, bus):
        """
        Set the bus instance for the timer.

        Args:
            bus: The Bus instance to be used.
        """
        self.bus = bus

    def get_bus(self):
        """
        Get the current bus instance.

        Returns:
            The Bus instance associated with the timer.
        """
        return self.bus

    def current_time(self):
        """
        Get the current time in ticks.

        Returns:
            int: The current time tick.
        """
        return self.ticks
