import os

from util.service_logging import log


class Config:
    bucket_name = "env_var_not_set"
    server_park = "env_var_not_set"
    blaise_api_url = "env_var_not_set"
    valid_surveys = ["OPN", "LMS"]
    extension_list = [".blix", ".bdbx", ".bdix", ".bmix"]
    bufsize = 10 * 1024 * 1024  # 10Mb

    @classmethod
    def from_env(cls):
        config = cls()
        config.server_park = os.getenv("SERVER_PARK", "env_var_not_set")
        config.blaise_api_url = os.getenv("BLAISE_API_URL", "env_var_not_set")
        config.bucket_name = os.getenv("NISRA_BUCKET_NAME", "env_var_not_set")
        return config

    def log(self):
        log.info(f"bucket_name - {self.bucket_name}")
        log.info(f"valid_surveys - {self.valid_surveys}")
        log.info(f"extension_list - {str(self.extension_list)}")
        log.info(f"server_park - {self.server_park}")
        log.info(f"blaise_api_url - {self.blaise_api_url}")

    def valid_survey_name(self, survey_name: str) -> bool:
        survey_prefix = survey_name.upper()[:3]
        survey_number = survey_name[3:7]
        return (
            survey_prefix in self.valid_surveys
            and survey_number.isnumeric()
            and len(survey_name) >= 7
        )
