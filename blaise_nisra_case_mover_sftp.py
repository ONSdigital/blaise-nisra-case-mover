import pysftp
from google.cloud import storage
import os


def establish_sftp_connection():
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:

            file_list = sftp.listdir('ONS/OPN/opn1911a')

            [sftp.get('ONS/OPN/opn1911a/' + file, file) for file in file_list]

            [upload_blob(bucket_name='nisra-transfer',
                         source_file_name=file,
                         destination_blob_name=file) for file in file_list]

    except Exception as err:
        print('Connection error:', err)
        raise

    return sftp


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


establish_sftp_connection()

exit(0)
