"""Google Cloud Storage Configuration."""
from os import environ
import os

survey_destination_path = environ.get('SURVEY_DESTINATION_PATH')
survey_source_path = environ.get('SURVEY_SOURCE_PATH_PREFIX') + survey_destination_path
bucket_name = environ.get('NISRA_BUCKET_NAME')

if 'AUDIT_TRAIL' in os.environ:
    audit_trail = environ.get('AUDIT_TRAIL')
    extension_list = '*.db'
else:
    extension_list = ('*.blix',
                      '*.badi',
                      '*.bdbx',
                      '*.bdix',
                      '*.bmix',
                      '*.manifest')