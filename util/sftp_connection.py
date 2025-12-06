import logging
from contextlib import contextmanager
from typing import Generator

import paramiko

from pkg.sftp import SFTPConfig


@contextmanager
def sftp_connection(
    sftp_config: SFTPConfig,
) -> Generator[paramiko.SFTPClient, None, None]:

    host = getattr(sftp_config, "host", "").lower()

    ssh = paramiko.SSHClient()

    # TODO: Set known host key for prod!
    logging.warning(f"⚠️ Accepting unknown host keys for {host}")

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(
        hostname=host,
        username=sftp_config.username,
        password=sftp_config.password,
        port=int(sftp_config.port),
        compress=True,
        look_for_keys=False,
        allow_agent=False,
    )

    transport = ssh.get_transport()
    if transport:
        transport.set_keepalive(30)

    try:
        with ssh.open_sftp() as sftp:
            yield sftp
    finally:
        ssh.close()
