import logging
from datetime import datetime, timezone
from typing import List

from services.blaise_service import BlaiseService
from services.google_bucket_service import GoogleBucketService
from services.notification_service import NotificationService


class NisraUpdateCheckService:
    def __init__(
            self,
            blaise_service: BlaiseService,
            bucket_service: GoogleBucketService,
            notification_service: NotificationService):
        self._survey_types_supported = "LMS"  # can be a tuple if we want to support more
        self._bucket_file_type = "bdbx"
        self._max_hours_since_last_update = 23
        self._blaise_service = blaise_service
        self._bucket_service = bucket_service
        self._notification_service = notification_service

    def check_nisra_files_have_updated(self) -> str:
        logging.info("Starting Nisra check service")

        questionnaire_names_in_blaise = self.get_names_of_questionnaire_in_blaise()
        questionnaire_modified_dates = self._bucket_service.get_questionnaire_modified_dates(self._bucket_file_type)

        for questionnaire_name in questionnaire_names_in_blaise:
            if questionnaire_name not in questionnaire_modified_dates:
                logging.warning(f"NisraUpdateCheckService - questionnaire {questionnaire_name} not in bucket")
                continue

            self.notify_if_questionnaire_has_not_been_updated(
                questionnaire_name,
                questionnaire_modified_dates[questionnaire_name])

        return "Done"

    def notify_if_questionnaire_has_not_been_updated(self, questionnaire_name: str, date_modified: datetime):

        if self.questionnaire_has_not_updated_within_max_hours(date_modified):
            logging.info(
                f"{questionnaire_name} has a modified date {date_modified} past {self._max_hours_since_last_update} hours, sending notification")

            self._notification_service.send_email_notification(questionnaire_name)

    def questionnaire_has_not_updated_within_max_hours(self, date_modified: datetime) -> bool:
        date_now = datetime.now(timezone.utc)
        hours_since_last_update = (date_modified - date_now).total_seconds() / 3600

        return hours_since_last_update > self._max_hours_since_last_update

    def get_names_of_questionnaire_in_blaise(self) -> List[str]:
        questionnaire_names = []
        questionnaires = self._blaise_service.get_questionnaires()
        for questionnaire in questionnaires:
            if not questionnaire['name'].upper().startswith(self._survey_types_supported):
                logging.info(f"instrument name {questionnaire['name']} not supported")
                continue

            questionnaire_names.append(questionnaire['name'].upper())
            logging.info(f"instrument name {questionnaire['name']} added")

        return questionnaire_names
