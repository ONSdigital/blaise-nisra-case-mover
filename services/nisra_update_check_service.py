import logging
from datetime import datetime, timezone
from typing import List

from services.blaise_service import BlaiseService
from services.google_bucket_service import GoogleBucketService


class NisraUpdateCheckService:
    def __init__(
            self,
            blaise_service: BlaiseService,
            bucket_service: GoogleBucketService):
        self._survey_types_supported = "LMS" # can be a tuple if we want to support more
        self._bucket_file_type = "bdbx"
        self._max_hours_since_last_update = 23
        self._blaise_service = blaise_service
        self._bucket_service = bucket_service

    def check_nisra_files_have_updated(self) -> str:
        logging.info("Starting Nisra check service")

        instrument_names_in_blaise = self.get_names_of_instruments_in_blaise()
        instruments_dates_dict = self._bucket_service.get_instrument_modified_dates_from_bucket(self._bucket_file_type)

        for instrument_name in instrument_names_in_blaise:
            if instrument_name not in instruments_dates_dict:
                logging.warning(f"NisraUpdateCheckService - instrument {instrument_name} not in bucket")
                continue

            date_modified = instruments_dates_dict[instrument_name]

            if self.instrument_has_not_updated_within_max_hours(date_modified, self._max_hours_since_last_update):
                logging.info(f"NisraUpdateCheckService: instrument {instrument_name} has not been updated in past {self._max_hours_since_last_update} hours")

        return "Done"

    @staticmethod
    def instrument_has_not_updated_within_max_hours(date_modified: datetime, max_hours: int) -> bool:
        date_now = datetime.now(timezone.utc)
        hours_since_last_update = (date_modified - date_now).total_seconds() / 3600

        return hours_since_last_update > max_hours

    def get_names_of_instruments_in_blaise(self) -> List[str]:
        instrument_names = []
        instruments = self._blaise_service.get_instruments()
        for instrument in instruments:
            if not instrument['name'].upper().startswith(self._survey_types_supported):
                logging.info(f"instrument name {instrument['name']} not supported")
                continue

            instrument_names.append(instrument['name'].upper())
            logging.info(f"instrument name {instrument['name']} added")

        return instrument_names


