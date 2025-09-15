import io
import stat
from dataclasses import dataclass
from typing import Any, Callable
from unittest import mock

import pytest

from pkg.config import Config
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTP, SFTPConfig


@pytest.fixture
def mock_sftp_connection():
    return mock.MagicMock()


@pytest.fixture
def sftp_config():
    return SFTPConfig(
        host="test_host",
        username="test_username",
        password="test_password",
        port="1234",
    )


@pytest.fixture
def config():
    return Config(
        bucket_name="test_bucket_name",
        server_park="MOCK_SERVER_PARK",
        blaise_api_url="mock_blaise_api_url.com",
        project_id="test_project_id",
        processor_topic_name="test_processor_topic_name",
    )


@pytest.fixture()
def mock_sftp(mock_sftp_connection, sftp_config, config):
    return SFTP(mock_sftp_connection, sftp_config, config)


@pytest.fixture
def google_storage(config: Any) -> GoogleStorage:
    return GoogleStorage(config.bucket_name)


@pytest.fixture
def mock_stat() -> Callable[[int], Any]:
    def inner(st_size: int) -> Any:
        @dataclass
        class MockStat:
            st_size: int

        return MockStat(st_size=st_size)

    return inner


@pytest.fixture
def mock_list_dir_attr() -> Callable[[str, int, int], Any]:
    def inner(filename: str, st_mtime: int, st_mode: int = stat.S_IFREG) -> Any:
        @dataclass
        class MockListDirAttr:
            filename: str
            st_mtime: int
            st_mode: int

        return MockListDirAttr(filename=filename, st_mtime=st_mtime, st_mode=st_mode)

    return inner


@pytest.fixture
def fake_sftp_file() -> Callable[[Any], Any]:
    def inner(contents: Any) -> Any:
        class FakeSFTPFile(io.BytesIO):
            def __init__(self, byte_content: Any) -> None:
                super().__init__(byte_content)

            def prefetch(self) -> None:
                pass

        return FakeSFTPFile(contents)

    return inner


@pytest.fixture
def fake_blob() -> Callable[[str], Any]:
    def inner(name: str) -> Any:
        @dataclass
        class FakeBlob:
            name: str

        return FakeBlob(name=name)

    return inner
