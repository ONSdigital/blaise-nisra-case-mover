import logging
from contextlib import contextmanager
import os
from typing import Generator

import paramiko

from pkg.sftp import SFTPConfig


@contextmanager
def sftp_connection(
    sftp_config: SFTPConfig, allow_unknown_hosts: bool = False
) -> Generator[paramiko.SFTPClient, None, None]:

    ssh = paramiko.SSHClient()

    if os.getenv("ENVIRONMENT", "prod").lower() in ("dev", "test", "local"):
        logging.warning(
            "Accepting unknown host keys! Only use this in test environments."
        )
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    else:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())

    ssh.connect(
        hostname=sftp_config.host,
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
