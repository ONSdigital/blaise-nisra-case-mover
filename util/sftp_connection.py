from contextlib import contextmanager

import paramiko

@contextmanager
def sftp_connection(sftp_config):
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=sftp_config.host,
        username=sftp_config.username,
        password=sftp_config.password,
        port=int(sftp_config.port),
        compress=True,
        look_for_keys=False,
        allow_agent=False
    )
    try:
        with ssh.open_sftp() as sftp:
            yield sftp
    finally:
        ssh.close()
