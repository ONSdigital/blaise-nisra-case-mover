from typing import List

from google.cloud import storage

from models.instrument_file_model import InstrumentFile


class GoogleStorage:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.get_bucket(self.bucket_name)

    def get_files(self) -> List[InstrumentFile]:
        instrument_files = []
        blobs = list(self.bucket.list_blobs())

        for blob in blobs:
            instrument_files.append(
                InstrumentFile(
                    file_name=blob.name,
                    last_updated=blob.updated))

        return instrument_files
