import logging
from typing import List

from google.cloud import storage

from models.configuration.bucket_config_model import BucketConfig
from models.instrument_file_model import InstrumentFile


class GoogleStorageService:
    def __init__(self, config: BucketConfig):
        self._bucket_name = config.bucket_name
        self.storage_client = storage.Client()

    def get_files(self, file_extension: str) -> List[InstrumentFile]:
        logging.info(f"GoogleStorageService - connect to bucket {self._bucket_name}")
        bucket = self.storage_client.get_bucket(self._bucket_name)

        instrument_files = []

        logging.info(f"GoogleStorageService - get blobs in bucket {self._bucket_name}")
        blobs = list(bucket.list_blobs())

        logging.info("Iterate over blobs in bucket")
        for blob in blobs:
            logging.info(f"Blob file name - {blob.name}")
            if blob.name.endswith(file_extension):
                logging.info(f"Add file name to list - {blob.name}")
                instrument_files.append(
                    InstrumentFile(
                        file_name=blob.name,
                        last_updated=blob.updated))

        logging.info(f"return instrument files {instrument_files}")
        return instrument_files
