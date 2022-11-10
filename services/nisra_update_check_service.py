import logging

from services.blaise_service import BlaiseService
from services.google_storage_service import GoogleStorageService


class NisraUpdateCheckService:
    def __init__(
            self,
            blaise_service: BlaiseService,
            bucket_service: GoogleStorageService):
        self._survey_types_supported = ["LMS"]
        self._max_hours_since_last_update = 23
        self._blaise_service = blaise_service
        self._bucket_service = bucket_service

    def check_nisra_files_have_updated(self) -> str:
        logging.info("Starting Nisra check service")

        try:
            instruments = self._blaise_service.get_instruments()
            for instrument in instruments:
                logging.info(f"instrument - {instrument['name']}")
        except Exception as error:
            logging.info("Error in getting instruments from blaise ", error)

        try:
            bucket_files = self._bucket_service.get_files("bdbx")
            for file in bucket_files:
                logging.info(f"Bucket file - {file.file_name} {file.last_updated}")
        except Exception as error:
            logging.info("Error in getting files from bucket", error)

        return "Done"

