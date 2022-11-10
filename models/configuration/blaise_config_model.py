import logging
import os
from dataclasses import dataclass


@dataclass
class BlaiseConfig:
    blaise_api_url: str
    server_park: str

    @classmethod
    def from_env(cls) -> "BlaiseConfig":
        return cls(
            blaise_api_url=os.getenv("BLAISE_API_URL", ""),
            server_park=os.getenv("SERVER_PARK", "")
        )

    def log(self) -> None:
        logging.info(f"Configuration - blaise_api_url: {self.blaise_api_url}")
        logging.info(f"Configuration - server_park: {self.server_park}")
