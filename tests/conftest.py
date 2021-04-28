import io
import stat
from dataclasses import dataclass
from unittest import mock

import pytest

from pkg.config import Config
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTP, SFTPConfig
from util.service_logging import log


@pytest.fixture
def mock_sftp_connection():
    return mock.MagicMock()


@pytest.fixture
def sftp_config():
    sftp_config = SFTPConfig()
    sftp_config.survey_source_path = "./ONS/OPN"
    return sftp_config


@pytest.fixture
def config():
    config = Config()
    config.blaise_api_url = "mock_blaise_api_url.com"
    config.server_park = "MOCK_SERVER_PARK"
    return config


@pytest.fixture()
def mock_sftp(mock_sftp_connection, sftp_config, config):
    return SFTP(mock_sftp_connection, sftp_config, config)


@pytest.fixture
def google_storage(config):
    return GoogleStorage(config.bucket_name, log)


@pytest.fixture
def mock_stat():
    def inner(st_size):
        @dataclass
        class MockStat:
            st_size: int

        return MockStat(st_size=st_size)

    return inner


@pytest.fixture
def mock_list_dir_attr():
    def inner(filename, st_mtime, st_mode=stat.S_IFREG):
        @dataclass
        class MockListDirAttr:
            filename: str
            st_mtime: int
            st_mode: int

        return MockListDirAttr(filename=filename, st_mtime=st_mtime, st_mode=st_mode)

    return inner


@pytest.fixture
def fake_sftp_file():
    def inner(contents):
        class FakeSFTPFile(io.BytesIO):
            def __init__(self, byte_content):
                super().__init__(byte_content)

            def prefetch(self):
                pass

        return FakeSFTPFile(contents)

    return inner
