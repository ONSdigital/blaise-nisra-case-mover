import logging
from typing import Dict

from notifications_python_client import NotificationsAPIClient

from models.configuration.notification_config_model import NotificationConfig


class NotificationService:
    def __init__(self, config: NotificationConfig):
        self._email_client = NotificationsAPIClient(config.notify_api_key)  # type: ignore
        self._email_address = config.nisra_notify_email

    def send_email_notification(
        self, message: Dict[str, str], template_id: str
    ) -> None:
        try:
            logging.info(
                f"Sending email notification {message} to {self._email_address}"
            )
            self._email_client.send_email_notification(  # type: ignore
                email_address=f"{self._email_address}",
                template_id=f"{template_id}",
                personalisation=message,
            )
        except Exception as error:
            logging.error(
                f"NotificationService: Error when sending email via GOV.UK Notify API - {error}"
            )
            raise error
