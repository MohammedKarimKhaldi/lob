from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

class EventType(Enum):
    """Types of events in the simulation."""
    ORDER = "order"
    CANCEL = "cancel"
    TRADE = "trade"
    MARKET_DATA = "market_data"

class Event(ABC):
    """Base class for all events in the simulation."""
    def __init__(self, event_type: EventType, timestamp: float):
        self.event_type = event_type
        self.timestamp = timestamp

    @abstractmethod
    def process(self) -> Any:
        """Process the event and return any results."""
        pass
