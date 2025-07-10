from typing import Optional
from .base import Event

class EventQueue:
    """Priority queue for managing events in chronological order."""
    def __init__(self):
        self.events = []
        self._event_counter = 0  # Unique counter for event queue tie-breaker

    def add_event(self, event: Event):
        """Add an event to the queue."""
        import heapq
        self._event_counter += 1
        heapq.heappush(self.events, (event.timestamp, self._event_counter, event))

    def get_next_event(self) -> Optional[Event]:
        """Get the next event from the queue."""
        import heapq
        if self.events:
            _, _, event = heapq.heappop(self.events)
            return event
        return None

    def peek_next_event(self) -> Optional[Event]:
        """Peek at the next event without removing it."""
        if self.events:
            _, _, event = self.events[0]
            return event
        return None

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return len(self.events) == 0

    def size(self) -> int:
        """Get the number of events in the queue."""
        return len(self.events)
