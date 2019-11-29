"""Google Cloud Storage Configuration."""
from os import environ


survey_destination_path = environ.get('SURVEY_DESTINATION_PATH')
survey_source_path = environ.get('SURVEY_SOURCE_PATH_PREFIX') + survey_destination_path
bucket_name = environ.get('NISRA_BUCKET_NAME')

file_list = ['FrameSOC2010.blix',
             'OPN1911a.badi',
             'OPN1911a.bdbx',
             'OPN1911a.bdix',
             'OPN1911a.bmix',
             'OPN1911a.manifest']
