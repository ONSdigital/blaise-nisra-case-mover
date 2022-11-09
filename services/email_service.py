from notifications_python_client import NotificationsAPIClient


class EmailService:
    def __init__(self, email_client: NotificationsAPIClient):
        self._email_client = email_client

    def send_email_notification(self, email_address: str, email_template_id: str, questionnaire_name: str) -> None:
        try:
            print(f"Sending email notification for questionnaire {questionnaire_name} to {email_address}")
            self._email_client.send_email_notification(
                email_address=f"{email_address}",
                template_id=f"{email_template_id}",
                personalisation={"questionnaire_name": questionnaire_name}
            )
        except Exception as error:
            print(
                f"Error when sending email notification for questionnaire {questionnaire_name} via GOV.UK Notify API - ",
                error)
