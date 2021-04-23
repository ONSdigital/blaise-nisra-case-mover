import math

import requests

from models import Instrument
from pkg.config import Config
from pkg.gcs_stream_upload import GCSObjectStreamUpload
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTP
from util.service_logging import log


class CaseMover:
    def __init__(self, google_storage: GoogleStorage, config: Config, sftp: SFTP):
        self.google_storage = google_storage
        self.config = config
        self.sftp = sftp

    def bdbx_md5_changed(self, instrument: Instrument) -> bool:
        blob_md5 = self.google_storage.get_blob_md5(instrument.get_bdbx_blob_filepath())
        return instrument.bdbx_md5 == blob_md5

    def sync_instrument(self, instrument: Instrument) -> None:
        blob_filepaths = instrument.get_blob_filepaths()
        for file in instrument.files:
            blob_filepath = blob_filepaths[file]
            sftp_path = f"{instrument.sftp_path}/{file}"
            log.info(f"Syncing file from SFTP: {sftp_path} to GCP: {blob_filepath}")
            self.sync_file(blob_filepath, sftp_path)

    def sync_file(self, blob_filepath: str, sftp_path: str) -> None:
        with GCSObjectStreamUpload(
            google_storage=self.google_storage,
            blob_name=blob_filepath,
            chunk_size=self.config.bufsize,
        ) as blob_stream:
            bdbx_details = self.sftp.sftp_connection.stat(sftp_path)
            chunks = math.ceil(bdbx_details.st_size / self.config.bufsize)
            sftp_file = self.sftp.sftp_connection.open(
                sftp_path, bufsize=self.config.bufsize
            )
            sftp_file.prefetch()
            for chunk in range(chunks):
                sftp_file.seek(chunk * self.config.bufsize)
                blob_stream.write(sftp_file.read(self.config.bufsize))

    def send_request_to_api(self, instrument_name):
        # added 10 second timeout exception pass to the api request
        # because the connection to the api was timing out before
        # it completed the work. this also allows parallel requests
        # to be made to the api.

        log.info(
            f"Sending request to {self.config.blaise_api_url} "
            + f"for instrument {instrument_name}"
        )
        try:
            requests.post(
                (
                    f"http://{self.config.blaise_api_url}/api/v1/serverparks/"
                    + f"{self.config.server_park}/instruments/{instrument_name}/data"
                ),
                headers={"content-type": "application/json"},
                json={"instrumentDataPath": instrument_name},
                timeout=10,
            )
        except requests.exceptions.ReadTimeout:
            pass
