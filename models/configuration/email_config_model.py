import logging
import os

from dataclasses import dataclass


@dataclass
class EmailConfig:
    notify_api_key: str
    to_notify_email: str

    @classmethod
    def from_env(cls):
        return cls(
            notify_api_key=os.getenv("NOTIFY_API_KEY", "env_var_not_set"),
            to_notify_email=os.getenv("TO_NOTIFY_EMAIL", "env_var_not_set"),
        )

    def log(self):
        logging.info(f"notify_api_key - {self.notify_api_key}")
        logging.info(f"to_notify_email - {self.to_notify_email}")
