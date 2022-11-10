from typing import List

from google.cloud import storage

from models.configuration.bucket_config_model import BucketConfig
from models.instrument_file_model import InstrumentFile


class GoogleStorageService:
    def __init__(self, config: BucketConfig):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(config.bucket_name)

    def get_files(self, file_extension: str) -> List[InstrumentFile]:
        instrument_files = []
        blobs = list(self.bucket.list_blobs())

        for blob in blobs:
            if blob.name.endswith(file_extension):
                instrument_files.append(
                    InstrumentFile(
                        file_name=blob.name,
                        last_updated=blob.updated))

        return instrument_files
