import logging
import os

from dataclasses import dataclass


@dataclass
class NotificationConfig:
    notify_api_key: str
    to_notify_email: str
    email_template_id: str

    @classmethod
    def from_env(cls):
        return cls(
            notify_api_key=os.getenv("NOTIFY_API_KEY", "env_var_not_set"),
            to_notify_email=os.getenv("TO_NOTIFY_EMAIL", "env_var_not_set"),
            email_template_id="94264180-7ebd-4ff9-8a27-52abb5949c78"
        )

    def log(self):
        logging.info(f"notify_api_key - {self.notify_api_key}")
        logging.info(f"to_notify_email - {self.to_notify_email}")