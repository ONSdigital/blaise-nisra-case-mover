import os
from dotenv import load_dotenv
from os import environ


load_dotenv()

instrument_source_path = os.getenv('INSTRUMENT_SOURCE_PATH')
survey_source_path = os.getenv('SURVEY_SOURCE_PATH')
instrument_destination_path = os.getenv('INSTRUMENT_DESTINATION_PATH')
bucket_name = os.getenv('NISRA_BUCKET_NAME')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'key.json'

instrument_regex = '^[a-zA-Z]{3}[0-9][0-9][0-9][0-9][a-zA-Z]$'

if 'AUDIT_TRAIL' in os.environ:
    audit_trail = environ.get('AUDIT_TRAIL')
    extension_list = '*.db'
else:
    extension_list = ['*.blix',
                      '*.bdbx',
                      '*.bdix',
                      '*.bmix']

dir = os.path.dirname(__file__)
os.chdir(os.path.join(dir, 'tmp'))
