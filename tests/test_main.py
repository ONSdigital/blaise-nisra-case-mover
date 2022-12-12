import logging
from unittest import mock

import pytest
import requests

from main import do_processor, do_trigger, public_ip_logger


def test_public_ip_logger(requests_mock, caplog):
    with caplog.at_level(logging.INFO):
        requests_mock.get(
            "https://checkip.amazonaws.com/", status_code=200, text="1.3.3.7"
        )
        public_ip_logger()
    assert ("root", logging.INFO, "Public IP address - 1.3.3.7") in caplog.record_tuples


def test_public_ip_logger_raises_exception(requests_mock, caplog):
    with caplog.at_level(logging.WARN):
        requests_mock.get("https://checkip.amazonaws.com/", exc=Exception)
        public_ip_logger()
    assert (
        "root",
        logging.WARN,
        "Unable to lookup public IP address",
    ) in caplog.record_tuples


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
