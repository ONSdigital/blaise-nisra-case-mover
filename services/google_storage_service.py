import logging
from datetime import datetime
from typing import Dict

from google.cloud import storage

from models.configuration.bucket_config_model import BucketConfig


class GoogleStorageService:
    def __init__(self, config: BucketConfig):
        self._bucket_name = config.bucket_name
        self.storage_client = storage.Client()

    def get_instrument_modified_dates_from_bucket(self, file_extension: str) -> Dict[str, datetime]:
        try:
            bucket = self.storage_client.get_bucket(self._bucket_name)

            instrument_files = {}

            blobs = list(bucket.list_blobs())

            for blob in blobs:
                if blob.name.upper().endswith(file_extension.upper()):
                    continue

                instrument_name = blob.name.upper().split("/")[0]
                instrument_files[instrument_name] = blob.updated

            return instrument_files
        except Exception as error:
            logging.error("GoogleStorageService: error in calling 'get_files_from_bucket'", error)
