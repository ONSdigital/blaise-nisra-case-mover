from contextlib import contextmanager
import logging

import paramiko


@contextmanager
def sftp_connection(sftp_config, allow_unknown_hosts: bool = False):

    ssh = paramiko.SSHClient()

    if allow_unknown_hosts or sftp_config.host in ("localhost", "127.0.0.1"):
        logging.warning("Accepting unknown host keys! Only use this in test environments.")
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    else:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        
    #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
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
