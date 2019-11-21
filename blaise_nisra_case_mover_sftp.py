import os
import pysftp
import filecmp
from google.cloud import storage


def establish_sftp_connection():
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:

            survey_destination_path = 'OPN/opn1911a/'
            survey_source_path = 'ONS/' + survey_destination_path

            bucket_name = 'nisra-transfer'

            # file_list = sftp.listdir(survey_path)
            file_list = ['opn1911a.manifest', 'opn1911a.badi']

            for file in file_list:
                print('Copying %s from SFTP server...', file)
                sftp.get(survey_source_path + file, file)

                upload_blob(bucket_name=bucket_name,
                            source_file_name=file,
                            destination_blob_name=survey_destination_path + file)

    except Exception as err:
        print('Connection error:', err)
        raise

    return


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    if blob.exists():
        print(blob.md5_hash())
        print('Replacing with new version of {}.'.format(
            destination_blob_name))
    else:
        print('Creating new file {}.'.format(
            destination_blob_name))

    blob.upload_from_filename(source_file_name)
    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))
    return


establish_sftp_connection()

exit(0)
