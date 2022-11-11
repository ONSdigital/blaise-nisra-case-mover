import logging
from datetime import datetime
from typing import Dict

from google.cloud import storage

from models.configuration.bucket_config_model import BucketConfig


class GoogleBucketService:
    def __init__(self, config: BucketConfig):
        self._bucket = storage.Client().get_bucket(config.bucket_name)

    def get_questionnaire_modified_dates(self, file_extension: str) -> Dict[str, datetime]:
        try:
            questionnaire_modified_dates = {}
            blobs = list(self._bucket.list_blobs())

            for blob in blobs:
                if blob.name.upper().endswith(file_extension.upper()):
                    continue

                questionnaire_name = blob.name.upper().split("/")[0]
                questionnaire_modified_dates[questionnaire_name] = blob.updated
            return questionnaire_modified_dates
        except Exception as error:
            logging.error("GoogleStorageService: error in calling 'get_files_from_bucket'", error)
