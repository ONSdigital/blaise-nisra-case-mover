import json
from datetime import datetime

from models import Instrument, ProcessorEvent


def test_processor_event_json():
    instrument = Instrument(sftp_path="", files=["foo.bdix"], bdbx_updated_at=datetime(2021, 1, 1, 0, 0))
    instrument_name = "foobar"
    processor_event_json = ProcessorEvent(instrument_name=instrument_name, instrument=instrument).json()
    assert json.loads(processor_event_json) == {
        "instrument_name": "foobar",
        "instrument": {
            "bdbx_md5": None,
            "bdbx_updated_at": "2021-01-01T00:00:00",
            "files": ["foo.bdix"],
            "sftp_path": "",
        },
    }


def test_processor_event_from_json():
    processor_event_json = """
    {
        "instrument_name": "foobar",
        "instrument": {
            "bdbx_md5": null,
            "bdbx_updated_at": "2021-01-01T00:00:00",
            "files": ["foo.bdix"],
            "sftp_path": ""
        }
    }
    """

    instrument = Instrument(sftp_path="", files=["foo.bdix"], bdbx_updated_at=datetime(2021, 1, 1, 0, 0))
    assert ProcessorEvent.from_json(processor_event_json) == ProcessorEvent(instrument_name="foobar", instrument=instrument)
