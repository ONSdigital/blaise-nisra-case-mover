import logging
import os

from dataclasses import dataclass


@dataclass
class NotificationConfig:
    notify_api_key: str
    nisra_notify_email: str
    email_template_id: str

    @classmethod
    def from_env(cls):
        return cls(
            notify_api_key=os.getenv("NOTIFY_API_KEY", ""),
            nisra_notify_email=os.getenv("NISRA_NOTIFY_EMAIL", ""),
            email_template_id="94264180-7ebd-4ff9-8a27-52abb5949c78"
        )

    def log(self):
        logging.info(f"notify_api_key - {self.notify_api_key}")
        logging.info(f"to_nisra_notify_emailnotify_email - {self.nisra_notify_email}")
