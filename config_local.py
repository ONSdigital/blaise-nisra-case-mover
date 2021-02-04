import os
from dotenv import load_dotenv
from os import environ

load_dotenv()

survey_source_path = os.getenv('SURVEY_SOURCE_PATH')
bucket_name = os.getenv('NISRA_BUCKET_NAME')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'key.json'

instrument_regex = '^[a-zA-Z]{3}[0-9][0-9][0-9][0-9][a-zA-Z]$'

extension_list = ['*.blix',
                  '*.bdbx',
                  '*.bdix',
                  '*.bmix']

dir = os.path.dirname(__file__)
os.chdir(os.path.join(dir, 'tmp'))
