import os

from dataclasses import dataclass


@dataclass
class Config:
    blaise_server_park: str
    blaise_api_url: str
    notify_api_key: str
    to_notify_email: str

    @classmethod
    def from_env(cls):
        return cls(
            blaise_server_park=os.getenv("BLAISE_SERVER_PARK"),
            blaise_api_url=os.getenv("BLAISE_API_URL"),
            notify_api_key=os.getenv("NOTIFY_API_KEY"),
            to_notify_email=os.getenv("TO_NOTIFY_EMAIL"),
        )

    def log(self):
        print(f"Configuration - blaise_server_park: {self.blaise_server_park}")
        print(f"Configuration - blaise_api_url: {self.blaise_api_url}")
        if self.notify_api_key is None or self.notify_api_key == "null":
            print("Configuration - notify_api_key: None / null")
        else:
            print("Configuration - notify_api_key: Provided")
        print(f"Configuration - to_notify_email: {self.to_notify_email}")
