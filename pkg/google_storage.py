import binascii
import logging
from typing import Any, List, Optional

import pybase64
from google.cloud import storage
from google.cloud.storage import Bucket, Client

# workaround to prevent file transfer timeouts
storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB


class GoogleStorage:
    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self.bucket: Optional[Bucket] = None
        self.storage_client: Optional[Client] = None

    def initialise_bucket_connection(self) -> None:
        try:
            logging.info(f"Connecting to bucket - {self.bucket_name}")
            storage_client = storage.Client()
            self.storage_client = storage_client
            self.bucket = storage_client.get_bucket(self.bucket_name)
            logging.info(f"Connected to bucket - {self.bucket_name}")
        except Exception as ex:
            logging.error("Connection to bucket failed - %s", ex)

    def upload_file(self, source: str, dest: str) -> None:
        if self.bucket is None:
            raise RuntimeError(
                "Bucket connection not initialized. Call initialise_bucket_connection() first."
            )
        blob_destination = self.bucket.blob(dest)
        logging.info(f"Uploading file - {source}")
        blob_destination.upload_from_filename(source)
        logging.info(f"Uploaded file - {source}")

    def get_blob(self, blob_location: str) -> Any:
        if self.bucket is None:
            raise RuntimeError(
                "Bucket connection not initialized. Call initialise_bucket_connection() first."
            )
        return self.bucket.get_blob(blob_location)

    def list_blobs(self) -> List:
        if self.bucket is None:
            raise RuntimeError(
                "Bucket connection not initialized. Call initialise_bucket_connection() first."
            )
        return list(self.bucket.list_blobs())

    def delete_blobs(self, blob_list: List) -> None:
        if self.bucket is None:
            raise RuntimeError(
                "Bucket connection not initialized. Call initialise_bucket_connection() first."
            )
        self.bucket.delete_blobs(blob_list)

    def get_blob_md5(self, blob_location: str) -> Optional[str]:
        if self.bucket is None:
            raise RuntimeError(
                "Bucket connection not initialized. Call initialise_bucket_connection() first."
            )
        blob = self.bucket.get_blob(blob_location)
        if not blob:
            logging.info(f"{blob_location} does not exist in bucket {self.bucket_name}")
            return None
        return binascii.hexlify(pybase64.urlsafe_b64decode(blob.md5_hash)).decode(
            "utf-8"
        )


def init_google_storage(config: Any) -> GoogleStorage:
    google_storage = GoogleStorage(config.bucket_name)
    google_storage.initialise_bucket_connection()
    return google_storage
