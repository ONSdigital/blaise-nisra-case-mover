import logging
from contextlib import contextmanager
from typing import Generator

import paramiko

from pkg.sftp import SFTPConfig


@contextmanager
def sftp_connection(
    sftp_config: SFTPConfig, allow_unknown_hosts: bool = False
) -> Generator[paramiko.SFTPClient, None, None]:
    """
    Paramiko SFTP connection helper.

    Behavior:
    - For dev/test/CI: automatically accepts unknown host keys, mimicking pysftp.
    - For production: uses RejectPolicy, secure connection.

    Environment variable:
        ALLOW_UNKNOWN_HOSTS=true -> allow unknown hosts (dev/test only)
    """
    host = getattr(sftp_config, "host", "").lower()

    ssh = paramiko.SSHClient()

    if allow_unknown_hosts or host in ("localhost", "127.0.0.1", "::1"):
        logging.warning(
            f"⚠️ Accepting unknown host keys for {host}. "
            "Only safe for dev/test environments."
        )

        policy = (
            paramiko.AutoAddPolicy()  # codeql: ignore [py/paramiko-missing-host-key-validation]
        )
        ssh.set_missing_host_key_policy(policy)

    else:
        # Production: reject unknown hosts
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
