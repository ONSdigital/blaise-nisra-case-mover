from unittest import mock

import pytest

from config import Config, SFTPConfig
from google_storage import GoogleStorage
from util.service_logging import log


@pytest.fixture
def mock_sftp():
    return mock.MagicMock()


@pytest.fixture
def sftp_config():
    return SFTPConfig()


@pytest.fixture
def config():
    config = Config()
    config.blaise_api_url = "MOCK_BLAISE_API_URL"
    config.server_park = "MOCK_SERVER_PARK"
    return config


@pytest.fixture
def google_storage(config):
    return GoogleStorage(config.bucket_name, log)
