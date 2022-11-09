from models.config_model import Config
from services.email_service import EmailService


class NisraUpdateCheckService:
    def __init__(self, config: Config, email_service: EmailService):
        self._config = config
        self._email_service = email_service
