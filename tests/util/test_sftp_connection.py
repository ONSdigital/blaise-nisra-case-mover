from unittest import mock

import paramiko
import pytest

# Import your helper
from util.sftp_connection import sftp_connection


# If you have SFTPConfig class
class SFTPConfig:
    host: str
    username: str
    password: str
    port: int

    def __init__(self, host, username, password, port):
        self.host = host
        self.username = username
        self.password = password
        self.port = port


@pytest.fixture
def mock_ssh_client(monkeypatch):
    """
    Patch paramiko.SSHClient so no real connection is made.
    """
    mock_ssh = mock.MagicMock(spec=paramiko.SSHClient)
    mock_sftp = mock.MagicMock(spec=paramiko.SFTPClient)

    # ssh.open_sftp() returns mock_sftp in context manager
    mock_ssh.open_sftp.return_value.__enter__.return_value = mock_sftp
    mock_ssh.open_sftp.return_value.__exit__.return_value = None

    # Patch SSHClient constructor to return our mock
    monkeypatch.setattr(paramiko, "SSHClient", lambda: mock_ssh)

    return mock_ssh, mock_sftp


def test_sftp_connection_dev(mock_ssh_client, monkeypatch):
    ssh, sftp = mock_ssh_client

    # Simulate dev environment
    monkeypatch.setenv("ALLOW_UNKNOWN_HOSTS", "true")

    config = SFTPConfig("localhost", "user", "pass", 22)

    with sftp_connection(config) as client:
        # Assert the returned object is our mock SFTP client
        assert client is sftp

    # Check connect was called correctly
    ssh.connect.assert_called_with(
        hostname="localhost",
        username="user",
        password="pass",
        port=22,
        compress=True,
        look_for_keys=False,
        allow_agent=False,
    )

    # AutoAddPolicy should be used
    ssh.set_missing_host_key_policy.assert_called()
    policy = ssh.set_missing_host_key_policy.call_args[0][0]
    assert isinstance(policy, paramiko.AutoAddPolicy)


def test_sftp_connection_prod(mock_ssh_client, monkeypatch):
    ssh, sftp = mock_ssh_client

    # Simulate production environment (unset)
    monkeypatch.delenv("ALLOW_UNKNOWN_HOSTS", raising=False)

    config = SFTPConfig("example.com", "user", "pass", 22)

    with sftp_connection(config) as client:
        assert client is sftp

    # RejectPolicy should be used
    ssh.set_missing_host_key_policy.assert_called()
    policy = ssh.set_missing_host_key_policy.call_args[0][0]
    assert isinstance(policy, paramiko.RejectPolicy)

    # connect called as expected
    ssh.connect.assert_called_with(
        hostname="example.com",
        username="user",
        password="pass",
        port=22,
        compress=True,
        look_for_keys=False,
        allow_agent=False,
    )
