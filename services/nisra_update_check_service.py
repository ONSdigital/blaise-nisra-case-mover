import logging

from services.ftp_service import FtpService
from services.google_storage_service import GoogleStorageService


class NisraUpdateCheckService:
    def __init__(
            self,
            bucket_service: GoogleStorageService,
            ftp_service: FtpService):
        self._survey_types_supported = ["LMS"]
        self._max_hours_since_last_update = 23
        self._bucket_service = bucket_service
        self._ftp_service = ftp_service

    def check_nisra_files_have_updated(self) -> str:
        logging.info("Starting Nisra check service")
        try:
            bucket_files = self._bucket_service.get_files("bdbx")
            for file in bucket_files:
                logging.info(f"Bucket file - {file.file_name} {file.last_updated}")
        except Exception as error:
            logging.info("Error in getting files from bucket", error)

        try:
            ftp_files = self._ftp_service.get_files("", "bdbx")
            for file in ftp_files:
                logging.info(f"Ftp file - {file.file_name} {file.last_updated}")
        except Exception as error:
            logging.info("Error in getting files from ftp ", error)

        return "Done"

