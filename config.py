import os
from os import environ

instrument_source_path = environ.get('INSTRUMENT_SOURCE_PATH')
survey_source_path = environ.get('SURVEY_SOURCE_PATH')
instrument_destination_path = environ.get('INSTRUMENT_DESTINATION_PATH')
bucket_name = environ.get('NISRA_BUCKET_NAME')

instrument_regex = '^[a-zA-Z]{3}[0-9][0-9][0-9][0-9][a-zA-Z]$'

if 'AUDIT_TRAIL' in os.environ:
    audit_trail = environ.get('AUDIT_TRAIL')
    extension_list = '*.db'
else:
    extension_list = ['*.blix',
                      '*.bdbx',
                      '*.bdix',
                      '*.bmix']
