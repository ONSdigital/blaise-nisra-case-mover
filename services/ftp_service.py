from datetime import datetime, timezone
from typing import List

import pysftp

from models.configuration.ftp_config_model import FtpConfig
from models.instrument_file_model import InstrumentFile


class FtpService:
    def __init__(self, config: FtpConfig) -> None:
        self.config = config

    def get_files(self, directory: str, file_extension: str) -> List[InstrumentFile]:
        instrument_files = []

        with self.get_sftp_connection() as connection:
            walktree_callbacks = pysftp.WTCallbacks()
            connection.walktree(
                directory,
                fcallback=walktree_callbacks.file_cb,
                dcallback=walktree_callbacks.dir_cb,
                ucallback=walktree_callbacks.unk_cb)

            for file_name in walktree_callbacks.flist:
                if not file_name.endswith(file_extension):
                    continue

                file_properties = connection.sftp_client.stat(file_name)
                instrument_files.append(
                    InstrumentFile(
                        file_name=file_name,
                        last_updated=datetime.fromtimestamp(file_properties.st_mtime, tz=timezone.utc)))

        return instrument_files

    def get_sftp_connection(self) -> pysftp.Connection:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        cnopts.compression = True

        return pysftp.Connection(
            host=self.config.host,
            username=self.config.username,
            password=self.config.password,
            port=int(self.config.port),
            cnopts=cnopts
        )

