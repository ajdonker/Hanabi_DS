from dataclasses import dataclass
from typing import Any, Optional
@dataclass
class CommandMessage:
    type: str
    action: str
    data: dict[str, Any]
    request_id: Optional[str] = None
    connection_id: Optional[str] = None