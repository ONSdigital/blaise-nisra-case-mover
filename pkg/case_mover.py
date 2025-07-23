import logging
import math
import pathlib
from typing import Dict, List

import redo
import requests

from models import Instrument
from pkg.config import Config
from pkg.gcs_stream_upload import GCSObjectStreamUpload
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTP


class CaseMover:
    def __init__(self, google_storage: GoogleStorage, config: Config, sftp: SFTP):
        self.google_storage = google_storage
        self.config = config
        self.sftp = sftp

    def instrument_needs_updating(self, instrument: Instrument) -> bool:
        return self.bdbx_md5_changed(instrument) or self.gcp_missing_files(instrument)

    def bdbx_md5_changed(self, instrument: Instrument) -> bool:
        blob_md5 = self.google_storage.get_blob_md5(instrument.get_bdbx_blob_filepath())
        return instrument.bdbx_md5 != blob_md5

    def gcp_missing_files(self, instrument: Instrument) -> bool:
        instrument_blobs = self.get_instrument_blobs(instrument)
        for file in instrument.files:
            if file.lower() not in instrument_blobs:
                return True
        return False

    def get_instrument_blobs(self, instrument: Instrument) -> List[str]:
        instrument_blobs = []
        for blob in self.google_storage.list_blobs():
            if pathlib.Path(blob.name).parent.name == instrument.gcp_folder():
                instrument_blobs.append(pathlib.Path(blob.name).name.lower())
        return instrument_blobs

    def sync_instrument(self, instrument: Instrument) -> None:
        blob_filepaths = instrument.get_blob_filepaths()
        for file in instrument.files:
            blob_filepath = blob_filepaths[file]
            sftp_path = f"{instrument.sftp_path}/{file}"
            logging.info(f"Syncing file from SFTP: {sftp_path} to GCP: {blob_filepath}")
            self.sync_file(blob_filepath, sftp_path)

    def sync_file(self, blob_filepath: str, sftp_path: str) -> None:
        def perform_sync():
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

        try:
            redo.retry(
                perform_sync,
                retry_exceptions=(requests.exceptions.ReadTimeout,),
                attempts=4,
                max_sleeptime=0,
            )

        except FileNotFoundError:
            logging.warning(
                f"File {sftp_path} not found on SFTP server; "
                "it seems to have been removed since getting the list of files "
                "from the server."
            )
        except Exception:
            logging.exception(
                f"Fatal error while syncing file {sftp_path} to {blob_filepath}"
            )

    def send_request_to_api(self, instrument_name: str) -> None:
        # added 1 second timeout exception pass to the api request
        # because the connection to the api was timing out before
        # it completed the work. this also allows parallel requests
        # to be made to the api.

        max_retries = 2
        attempt = 0

        logging.info(
            f"Sending request to {self.config.blaise_api_url} "
            + f"for instrument {instrument_name}"
        )
        while attempt <= max_retries:
            try:
                requests.post(
                    (
                        f"http://{self.config.blaise_api_url}/api/v2/serverparks/"
                        + f"{self.config.server_park}/questionnaires/{instrument_name}/data"
                    ),
                    headers={"content-type": "application/json"},
                    json={"questionnaireDataPath": instrument_name},
                    timeout=(2, 2),
                )
                logging.info(
                    f"Attempt {attempt + 1} successful for Instrument {instrument_name}"
                )
                break
            except (
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ReadTimeout,
            ) as e:
                logging.warning(
                    f"Attempt {attempt + 1} failed for Instrument {instrument_name} due to timeout: {e}"
                )
                attempt += 1
                pass

    def instrument_exists_in_blaise(self, instrument_name: str) -> bool:
        response = requests.get(
            f"http://{self.config.blaise_api_url}/api/v2/serverparks/"
            + f"{self.config.server_park}/questionnaires/{instrument_name}/exists"
        )
        return response.json()

    def filter_existing_instruments(
        self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        filtered_instruments = {}
        for key, instrument in instruments.items():
            if self.instrument_exists_in_blaise(instrument.gcp_folder()):
                logging.info(f"Instrument {instrument.gcp_folder()} exists in blaise")
                filtered_instruments[key] = instrument
            else:
                logging.info(
                    f"Instrument {instrument.gcp_folder()} does not exist in blaise, "
                    "not ingesting..."
                )
        return filtered_instruments
