import os

from dotenv import load_dotenv

load_dotenv()

survey_source_path = os.getenv('survey_source_path', 'env_var_not_set')
bucket_name = os.getenv('nisra_bucket_name', 'env_var_not_set')
sftp_host = os.getenv('sftp_host', 'env_var_not_set')
sftp_username = os.getenv('sftp_username', 'env_var_not_set')
sftp_password = os.getenv('sftp_password', 'env_var_not_set')
sftp_port = os.getenv('sftp_port', 'env_var_not_set')
blaise_api_url = os.getenv('blaise_api_url', 'env_var_not_set')
server_park = os.getenv('server_park', 'env_var_not_set')

os.environ["google_application_credentials"] = 'key.json'

instrument_regex = '^[a-zA-Z]{3}[0-9][0-9][0-9][0-9][a-zA-Z]$'

extension_list = ['*.blix',
                  '*.bdbx',
                  '*.bdix',
                  '*.bmix']

dir = os.path.dirname(__file__)
os.chdir(os.path.join(dir, 'tmp'))
