import os
from dotenv import load_dotenv

load_dotenv()

instrument_source_path = os.getenv('INSTRUMENT_SOURCE_PATH')
survey_source_path = os.getenv('SURVEY_SOURCE_PATH')
instrument_destination_path = os.getenv('INSTRUMENT_DESTINATION_PATH')
bucket_name = os.getenv('NISRA_BUCKET_NAME')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'key.json'
