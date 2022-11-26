import logging
from unittest import mock

import pytest

from main import do_processor, do_trigger


@mock.patch("main.TriggerEvent.from_json", side_effect=Exception("Kaboom"))
def test_do_trigger_exits_with_1_when_an_exception_is_raised(_from_json):
    with pytest.raises(SystemExit) as e:
        do_trigger(dict(data=""), {})

    assert e.value.code == 1


@mock.patch("main.TriggerEvent.from_json")
def test_do_trigger_logs_error_when_exception_is_raised(from_json, caplog):
    original_exception = Exception("Kaboom")

    from_json.side_effect = original_exception

    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit):
            do_trigger(dict(data=""), {})

    errors = [entry for entry in caplog.records if entry.levelno == logging.ERROR]
    assert len(errors) is 1
    error = errors[0]
    assert error.message == "Exception: Kaboom"
    assert error.exc_info[1] == original_exception


@mock.patch("main.Config.from_env", side_effect=Exception("Kaboom"))
def test_do_processor_exits_with_1_when_an_exception_is_raised(_from_env):
    with pytest.raises(SystemExit) as e:
        do_processor(dict(data=""), {})

    assert e.value.code == 1


@mock.patch("main.Config.from_env")
def test_do_processor_logs_error_when_exception_is_raised(from_env, caplog):
    original_exception = Exception("Kaboom")

    from_env.side_effect = original_exception

    with caplog.at_level(logging.ERROR):
        with pytest.raises(SystemExit):
            do_processor(dict(data=""), {})

    errors = [entry for entry in caplog.records if entry.levelno == logging.ERROR]
    assert len(errors) is 1
    error = errors[0]
    assert error.message == "Exception: Kaboom"
    assert error.exc_info[1] == original_exception
