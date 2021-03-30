import os


class SFTPConfig:
    host = os.getenv("SFTP_HOST", "env_var_not_set")
    username = os.getenv("SFTP_USERNAME", "env_var_not_set")
    password = os.getenv("SFTP_PASSWORD", "env_var_not_set")
    port = os.getenv("SFTP_PORT", "env_var_not_set")
    survey_source_path = os.getenv("SURVEY_SOURCE_PATH", "env_var_not_set")


class Config:
    bucket_name = os.getenv("NISRA_BUCKET_NAME", "env_var_not_set")
    instrument_regex = "^[a-zA-Z]{3}[0-9][0-9][0-9][0-9][a-zA-Z]$"
    extension_list = ["*.blix", "*.bdbx", "*.bdix", "*.bmix"]
    server_park = os.getenv("SERVER_PARK", "env_var_not_set")
    blaise_api_url = os.getenv("BLAISE_API_URL", "env_var_not_set")


if os.getenv("FLASK_ENV", "env_var_not_set") == "development":
    os.environ["google_application_credentials"] = "key.json"
    directory = os.path.dirname(__file__)
    os.chdir(os.path.join(directory, "tmp"))
elif os.getenv("FLASK_ENV", "env_var_not_set") == "testing":
    os.environ["google_application_credentials"] = "key.json"
else:
    os.chdir("/tmp")
