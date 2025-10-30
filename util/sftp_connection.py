import logging
from contextlib import contextmanager
from typing import Generator

import paramiko

from pkg.sftp import SFTPConfig


@contextmanager
def sftp_connection(sftp_config: SFTPConfig) -> Generator[paramiko.SFTPClient, None, None]:
    """
    Paramiko SFTP connection helper.

    Behavior:
    - Automatically accepts unknown host keys, mimicking pysftp.
    """
    host = getattr(sftp_config, "host", "").lower()

    ssh = paramiko.SSHClient()

    logging.warning(f"⚠️ Accepting unknown host keys for {host}. Only safe for dev/test/ci environment.")

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # codeql: ignore [py/paramiko-missing-host-key-validation]

    ssh.connect(
        hostname=host,
        username=sftp_config.username,
        password=sftp_config.password,
        port=int(sftp_config.port),
        compress=True,
        look_for_keys=False,
        allow_agent=False,
    )
    try:
        with ssh.open_sftp() as sftp:
            yield sftp
    finally:
        ssh.close()
