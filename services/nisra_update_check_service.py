from models.config_model import Config
from services.email_service import EmailService


class NisraUpdateCheckService:
    def __init__(self, config: Config, email_service: EmailService):
        self._config = config
        self._email_service = email_service
        self._survey_types_supported = ["LMS"]
        self._max_hours_since_last_update = 23

    def check_nisra_files_have_updated(self) -> str:
        # get a list of active instruments

        # get a list of files in GCP bucket

        # send email if time difference is greater than max allowed

        return "Done"

