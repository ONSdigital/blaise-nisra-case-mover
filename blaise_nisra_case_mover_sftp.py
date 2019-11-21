import pysftp
from google.cloud import storage
import os
import logging


def establish_sftp_connection():
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:

            survey_path = 'ONS/OPN/opn1911a'
            bucket_name = 'nisra-transfer'

            file_list = sftp.listdir(survey_path)
            create_blob_structure(bucket_name=bucket_name,
                                  survey_path=survey_path)

            for file in file_list:
                logging.info('Copying %s from SFTP server...', file)
                sftp.get(survey_path + '/' + file, file)

                upload_blob(bucket_name=bucket_name,
                            source_file_name=file,
                            destination_blob_name=survey_path + '/' + file)

    except Exception as err:
        print('Connection error:', err)
        raise

    return


def create_blob_structure(bucket_name, survey_path):

    upload_blob(bucket_name=bucket_name,
                source_file_name=survey_path,
                destination_blob_name=survey_path)
    return


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))
    return


establish_sftp_connection()

exit(0)
