import os
from dataclasses import dataclass


@dataclass
class NotificationConfig:
    notify_api_key: str
    nisra_notify_email: str

    @classmethod
    def from_env(cls):
        return cls(
            notify_api_key=os.getenv("NOTIFY_API_KEY", ""),
            nisra_notify_email=os.getenv("NISRA_NOTIFY_EMAIL", ""),
        )
