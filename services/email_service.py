from notifications_python_client import NotificationsAPIClient

from models.configuration.email_config_model import EmailConfig


class EmailService:
    def __init__(self, config: EmailConfig):
        self._email_client = NotificationsAPIClient(config.notify_api_key)
        self._email_address = config.to_notify_email
        self._email_template_id = "94264180-7ebd-4ff9-8a27-52abb5949c78"

    def send_email_notification(self, questionnaire_name: str) -> None:
        try:
            print(f"Sending email notification for questionnaire {questionnaire_name} to {self._email_address}")
            self._email_client.send_email_notification(
                email_address=f"{self._email_address}",
                template_id=f"{self._email_template_id}",
                personalisation={"questionnaire_name": questionnaire_name}
            )
        except Exception as error:
            print(
                f"Error when sending email for questionnaire {questionnaire_name} via GOV.UK Notify API - ", error)
