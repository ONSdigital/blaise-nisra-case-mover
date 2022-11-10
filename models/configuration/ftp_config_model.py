import logging
import os


class FtpConfig:
    host = None
    username = None
    password = None
    port = None
    survey_source_path = None

    @classmethod
    def from_env(cls):
        cls.host = os.getenv("SFTP_HOST", "env_var_not_set")
        cls.username = os.getenv("SFTP_USERNAME", "env_var_not_set")
        cls.password = os.getenv("SFTP_PASSWORD", "env_var_not_set")
        cls.port = os.getenv("SFTP_PORT", "env_var_not_set")
        cls.survey_source_path = os.getenv("SURVEY_SOURCE_PATH", "env_var_not_set")
        return cls()

    def log(self):
        logging.info(f"survey_source_path - {self.survey_source_path}")
        logging.info(f"sftp_host - {self.host}")
        logging.info(f"sftp_port - {self.port}")
        logging.info(f"sftp_username - {self.username}")