import logging
import os
from dataclasses import dataclass, field
from typing import List, Type, TypeVar

from paramiko.common import DEFAULT_WINDOW_SIZE

T = TypeVar("T", bound="Config")


@dataclass
class Config:
    bucket_name: str
    server_park: str
    blaise_api_url: str
    project_id: str
    processor_topic_name: str
    valid_surveys: List[str] = field(default_factory=lambda: ["OPN", "LMS", "WLS"])
    extension_list: List[str] = field(
        default_factory=lambda: [".blix", ".bdbx", ".bdix", ".bmix"]
    )
    bufsize: int = field(default_factory=lambda: DEFAULT_WINDOW_SIZE)

    @classmethod
    def from_env(cls: Type[T]) -> T:
        missing = []

        def get_from_env(name: str) -> str:
            try:
                return os.environ[name]
            except KeyError:
                missing.append(name)
                return ""

        instance = cls(
            server_park=get_from_env("SERVER_PARK"),
            blaise_api_url=get_from_env("BLAISE_API_URL"),
            bucket_name=get_from_env("NISRA_BUCKET_NAME"),
            project_id=get_from_env("PROJECT_ID"),
            processor_topic_name=get_from_env("PROCESSOR_TOPIC_NAME"),
        )

        if missing:
            raise Exception(
                "The following required environment variables have not been set: "
                + ", ".join(missing)
            )

        return instance

    def log(self):
        logging.info(f"bucket_name - {self.bucket_name}")
        logging.info(f"valid_surveys - {self.valid_surveys}")
        logging.info(f"extension_list - {str(self.extension_list)}")
        logging.info(f"server_park - {self.server_park}")
        logging.info(f"blaise_api_url - {self.blaise_api_url}")
        logging.info(f"project_id - {self.project_id}")
        logging.info(f"processor_topic_name - {self.processor_topic_name}")

    def valid_survey_name(self, survey_name: str) -> bool:
        survey_prefix = survey_name.upper()[:3]
        survey_number = survey_name[3:7]
        return (
            survey_prefix in self.valid_surveys
            and survey_number.isnumeric()
            and len(survey_name) >= 7
        )
