import os

from dotenv import load_dotenv

load_dotenv()

survey_source_path = os.getenv("SURVEY_SOURCE_PATH", "env_var_not_set")
bucket_name = os.getenv("NISRA_BUCKET_NAME", "env_var_not_set")
sftp_host = os.getenv("SFTP_HOST", "env_var_not_set")
sftp_username = os.getenv("SFTP_USERNAME", "env_var_not_set")
sftp_password = os.getenv("SFTP_PASSWORD", "env_var_not_set")
sftp_port = os.getenv("SFTP_PORT", "env_var_not_set")

instrument_regex = "^[a-zA-Z]{3}[0-9][0-9][0-9][0-9][a-zA-Z]$"

extension_list = ["*.blix", "*.bdbx", "*.bdix", "*.bmix"]

if os.getenv("FLASK_ENV", "env_var_not_set") == "development":
    os.environ["google_application_credentials"] = "key.json"
    directory = os.path.dirname(__file__)
    os.chdir(os.path.join(directory, "tmp"))
elif os.getenv("FLASK_ENV", "env_var_not_set") == "testing":
    os.environ["google_application_credentials"] = "key.json"
else:
    os.chdir("/tmp")
