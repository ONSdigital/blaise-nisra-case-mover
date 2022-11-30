import logging
from unittest import mock

from main import do_processor, do_trigger


@mock.patch("main.TriggerEvent.from_json")
def test_do_trigger_logs_error_when_exception_is_raised(from_json, caplog):
    original_exception = Exception("Kaboom")

    from_json.side_effect = original_exception

    with caplog.at_level(logging.ERROR):
        do_trigger(dict(data=""), {})

    errors = [entry for entry in caplog.records if entry.levelno == logging.ERROR]
    assert len(errors) == 1
    error = errors[0]
    assert error.message == "Exception: Kaboom"
    assert error.exc_info[1] == original_exception


@mock.patch("main.Config.from_env")
def test_do_processor_logs_error_when_exception_is_raised(from_env, caplog):
    original_exception = Exception("Kaboom")

    from_env.side_effect = original_exception

    with caplog.at_level(logging.ERROR):
        do_processor(dict(data=""), {})

    errors = [entry for entry in caplog.records if entry.levelno == logging.ERROR]
    assert len(errors) == 1
    error = errors[0]
    assert error.message == "Exception: Kaboom"
    assert error.exc_info[1] == original_exception
