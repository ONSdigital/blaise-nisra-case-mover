import json
from dataclasses import asdict, dataclass

from dacite import from_dict


@dataclass
class TriggerEvent:
    survey: str

    def json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_object: str) -> "TriggerEvent":
        return from_dict(data_class=cls, data=json.loads(json_object))
