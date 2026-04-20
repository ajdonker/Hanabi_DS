from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Event:
    event: str
    data: dict[str, Any]