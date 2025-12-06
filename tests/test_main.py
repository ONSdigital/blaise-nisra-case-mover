import logging
from unittest import mock

import flask
import pytest

from main import do_processor, do_trigger, public_ip_logger


def test_public_ip_logger(requests_mock, caplog):
    with caplog.at_level(logging.INFO):
        requests_mock.get(
            "https://checkip.amazonaws.com/", status_code=200, text="1.3.3.7"
        )
        public_ip_logger()
    assert ("root", logging.INFO, "Public IP address - 1.3.3.7") in caplog.record_tuples


def test_public_ip_logger_logs_warning(requests_mock, caplog):
    with caplog.at_level(logging.WARN):
        requests_mock.get("https://checkip.amazonaws.com/", exc=Exception)
        public_ip_logger()
    assert (
        "root",
        logging.WARN,
        "Unable to lookup public IP address",
    ) in caplog.record_tuples


@mock.patch("flask.Request.get_json")
def test_do_trigger_logs_error_when_exception_is_raised(mock_get_json, caplog):
    # arrange
    mock_get_json.side_effect = Exception("Kaboom")
    request = flask.Request.from_values(json={"survey": "OPN"})

    # act
    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="Kaboom"):
            do_trigger(request)

    # assert
    errors = [entry for entry in caplog.records if entry.levelno == logging.ERROR]
    assert len(errors) == 1
    error = errors[0]
    assert error.message == "Exception: Kaboom"


@mock.patch("main.Config.from_env")
def test_do_processor_logs_error_when_exception_is_raised(from_env, caplog):
    original_exception = Exception("Kaboom")
    from_env.side_effect = original_exception

    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="Kaboom"):
            do_processor(dict(data=""), {})

    errors = [entry for entry in caplog.records if entry.levelno == logging.ERROR]
    assert len(errors) == 1
    error = errors[0]
    assert error.message == "Exception: Kaboom"


def test_do_trigger_bucket_none(monkeypatch, sftp_config, config, google_storage):
    monkeypatch.setattr("main.SFTPConfig.from_env", lambda: sftp_config)
    monkeypatch.setattr("main.Config.from_env", lambda: config)

    google_storage.bucket = None
    monkeypatch.setattr("main.init_google_storage", lambda config: google_storage)
    monkeypatch.setattr("main.SFTP", mock.MagicMock)
    monkeypatch.setattr("main.CaseMover", mock.MagicMock)
    monkeypatch.setattr("main.get_filtered_instruments", lambda *a, **k: {})
    monkeypatch.setattr("main.pubsub_v1.PublisherClient", lambda: mock.MagicMock())

    request = mock.MagicMock()
    request.get_json.return_value = {"survey": "TEST_SURVEY"}

    result, status = do_trigger(request)

    assert status == 500
    assert "Connection to bucket failed" in result


def test_do_trigger_bucket_exists(monkeypatch, sftp_config, config, google_storage):
    monkeypatch.setattr("main.Config.from_env", lambda: config)
    monkeypatch.setattr("main.SFTPConfig.from_env", lambda: sftp_config)

    google_storage.bucket = config.bucket_name
    monkeypatch.setattr("main.init_google_storage", lambda config: google_storage)

    # Mock the SFTP connection context manager
    mock_sftp_conn = mock.MagicMock()

    class MockSFTPConnection:
        def __enter__(self):
            return mock_sftp_conn

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        "main.sftp_connection", lambda *args, **kwargs: MockSFTPConnection()
    )

    # Mock SFTP and CaseMover classes
    monkeypatch.setattr("main.SFTP", lambda *args, **kwargs: mock.MagicMock())
    monkeypatch.setattr("main.CaseMover", lambda *args, **kwargs: mock.MagicMock())

    # Mock to return instruments
    mock_instrument = mock.MagicMock()

    def mock_get_filtered(*args, **kwargs):
        print("get_filtered_instruments called!")  # Debug print
        return {"TEST_INSTRUMENT": mock_instrument}

    monkeypatch.setattr("main.get_filtered_instruments", mock_get_filtered)
    monkeypatch.setattr("main.trigger_processor", lambda *args, **kwargs: None)

    request = mock.MagicMock()
    request.get_json.return_value = {"survey": "TEST_SURVEY"}

    result = do_trigger(request)
    print(f"Result: {result}")  # Debug print
    assert result == "Done"
