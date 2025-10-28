import logging
from unittest import mock

import paramiko

from pkg.sftp import SFTPConfig
from util.sftp_connection import sftp_connection


def test_sftp_connection_dev(caplog, monkeypatch):

    mock_ssh = mock.MagicMock()
    mock_sftp = mock.MagicMock()

    mock_sftp_context = mock.MagicMock()
    mock_sftp_context.__enter__.return_value = mock_sftp

    mock_ssh.open_sftp.return_value = mock_sftp_context
    mock_ssh.connect.return_value = None

    monkeypatch.setattr("paramiko.SSHClient", lambda: mock_ssh)

    monkeypatch.setenv("ALLOW_UNKNOWN_HOSTS", "true")
    config = SFTPConfig("localhost", "user", "pass", 22)

    with caplog.at_level(logging.WARNING):
        with sftp_connection(config) as client:
            assert client is mock_sftp

    assert any("Accepting unknown host keys" in msg for msg in caplog.messages)

    mock_ssh.connect.assert_called_with(
        hostname="localhost",
        username="user",
        password="pass",
        port=22,
        compress=True,
        look_for_keys=False,
        allow_agent=False,
    )

    mock_ssh.set_missing_host_key_policy.assert_called()
    policy = mock_ssh.set_missing_host_key_policy.call_args[0][0]
    assert isinstance(policy, paramiko.AutoAddPolicy)


def test_sftp_connection_prod(monkeypatch):

    mock_ssh = mock.MagicMock()
    mock_sftp = mock.MagicMock()

    mock_sftp_context = mock.MagicMock()
    mock_sftp_context.__enter__.return_value = mock_sftp

    mock_ssh.open_sftp.return_value = mock_sftp_context

    monkeypatch.setattr("paramiko.SSHClient", lambda: mock_ssh)
    mock_ssh.connect.return_value = None

    monkeypatch.delenv("ALLOW_UNKNOWN_HOSTS", raising=False)

    config = SFTPConfig("example.com", "user", "pass", 22)

    with sftp_connection(config) as client:
        assert client is mock_sftp

    mock_ssh.set_missing_host_key_policy.assert_called()
    policy = mock_ssh.set_missing_host_key_policy.call_args[0][0]
    assert isinstance(policy, paramiko.RejectPolicy)

    mock_ssh.connect.assert_called_with(
        hostname="example.com",
        username="user",
        password="pass",
        port=22,
        compress=True,
        look_for_keys=False,
        allow_agent=False,
    )
