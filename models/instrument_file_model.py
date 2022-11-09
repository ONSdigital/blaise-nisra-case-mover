from dataclasses import dataclass
from datetime import datetime


@dataclass
class InstrumentFile:
    file_name: str
    last_updated: datetime
