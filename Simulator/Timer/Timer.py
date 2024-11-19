from typing import List
import sys

class Timerr:
    def __init__(self):
        self.ticks = 0
        self.observers = []  #observers of timer ticks
        self.bus = None

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
            bool: True if all observers are active, False if any observer stops.
        """
        self.ticks += 1
        return self.notify(self.ticks)

    def notify(self, now):
        """
        Notify all observers about the current time tick.

        Args:
            now (int): Current time tick.

        Returns:
            bool: True if all observers are still active, False if any have completed their tasks.
        """
        inactive_count = 0
        for observer in self.observers:
            if not observer.update(now):
                inactive_count += 1

        # Propagate bus requests and replies
        if self.bus:
            self.bus.propagate_requests()
            self.bus.propagate_replies()

        # Return False if any observers are inactive
        return inactive_count == 0

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
