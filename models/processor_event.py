import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any

from dacite import from_dict

from models import Instrument


def json_serialiser(obj: Any) -> str:
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def json_decode_hook(obj: Any) -> Any:
    for key, value in obj.items():
        try:
            obj[key] = datetime.fromisoformat(value)
        except Exception:
            pass
    return obj


@dataclass
class ProcessorEvent:
    instrument_name: str
    instrument: Instrument

    def json(self) -> str:
        return json.dumps(asdict(self), default=json_serialiser)

    @classmethod
    def from_json(cls, json_object: str) -> "ProcessorEvent":
        return from_dict(
            data_class=cls, data=json.loads(json_object, object_hook=json_decode_hook)
        )
