import os
from dotenv import load_dotenv
from os import environ

load_dotenv()

survey_source_path = os.getenv('SURVEY_SOURCE_PATH', 'ENV_NOT_SET')
bucket_name = os.getenv('NISRA_BUCKET_NAME', 'ENV_NOT_SET')
SFTP_HOST = os.getenv('SFTP_HOST', 'ENV_NOT_SET')
SFTP_USERNAME = os.getenv('SFTP_USERNAME', 'ENV_NOT_SET')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD', 'ENV_NOT_SET')
SFTP_PORT = os.getenv('SFTP_PORT', 'ENV_NOT_SET')
BLAISE_API_URL = os.getenv('BLAISE_API_URL', 'ENV_NOT_SET')
SERVER_PARK = os.getenv('SERVER_PARK', 'ENV_NOT_SET')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'key.json'

instrument_regex = '^[a-zA-Z]{3}[0-9][0-9][0-9][0-9][a-zA-Z]$'

extension_list = ['*.blix',
                  '*.bdbx',
                  '*.bdix',
                  '*.bmix']

dir = os.path.dirname(__file__)
os.chdir(os.path.join(dir, 'tmp'))
