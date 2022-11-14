import logging

from notifications_python_client import NotificationsAPIClient

from models.configuration.notification_config_model import NotificationConfig


class NotificationService:
    def __init__(self, config: NotificationConfig):
        self._email_client = NotificationsAPIClient(config.notify_api_key)
        self._email_address = config.nisra_notify_email
        self._email_template_id = config.email_template_id

    def send_email_notification(self, questionnaire_name: str) -> None:
        try:
            logging.info(f"Sending email notification for questionnaire {questionnaire_name} to {self._email_address}")
            self._email_client.send_email_notification(
                email_address=f"{self._email_address}",
                template_id=f"{self._email_template_id}",
                personalisation={"questionnaire_name": questionnaire_name}
            )
        except Exception as error:
            logging.error(
                f"NotificationService: Error when sending email for questionnaire {questionnaire_name} "
                f"via GOV.UK Notify API - {error}")
