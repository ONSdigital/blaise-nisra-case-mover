import logging
from datetime import datetime, timezone

from services.blaise_service import BlaiseService
from services.google_bucket_service import GoogleBucketService
from services.notification_service import NotificationService


class NisraUpdateCheckService:
    def __init__(
            self,
            blaise_service: BlaiseService,
            bucket_service: GoogleBucketService,
            notification_service: NotificationService):
        self._survey_type = "LMS"
        self._bucket_file_type = "bdbx"
        self._max_hours_since_last_update = 23
        self._blaise_service = blaise_service
        self._bucket_service = bucket_service
        self._notification_service = notification_service

    def check_nisra_files_have_updated(self) -> str:
        questionnaire_names_in_blaise = self._blaise_service.get_names_of_questionnaire_in_blaise(self._survey_type)
        questionnaire_dates_in_bucket = self._bucket_service.get_questionnaire_modified_dates(self._bucket_file_type)

        for questionnaire_name in questionnaire_names_in_blaise:
            if questionnaire_name not in questionnaire_dates_in_bucket:
                logging.warning(f"{questionnaire_name} not in bucket")
                continue

            self.notify_if_questionnaire_has_not_been_updated(
                questionnaire_name,
                questionnaire_dates_in_bucket[questionnaire_name])

        return "Done"

    def notify_if_questionnaire_has_not_been_updated(self, questionnaire_name: str, date_modified: datetime) -> None:
        if self.questionnaire_has_not_updated_within_max_hours(date_modified):
            logging.info(
                f"{questionnaire_name} has a modified date {date_modified} past {self._max_hours_since_last_update} "
                f"hours, sending notification")

            self._notification_service.send_email_notification(questionnaire_name)

    def questionnaire_has_not_updated_within_max_hours(self, date_modified: datetime) -> bool:
        date_now = datetime.now(timezone.utc)
        hours_since_last_update = (date_now - date_modified).total_seconds() / 3600

        return hours_since_last_update > self._max_hours_since_last_update
