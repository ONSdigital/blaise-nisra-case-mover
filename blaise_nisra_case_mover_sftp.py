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
            print(sftp.listdir('ONS/OPN/opn1911a'))

            sftp.get('ONS/OPN/opn1911a/OPN1911a.manifest', 'OPN1911a.manifest')
            source_file_name = 'OPN1911a.manifest'
            destination_blob_name = 'OPN1911a.manifest'
            upload_blob(bucket_name='nisra-transfer',
                        source_file_name=source_file_name,
                        destination_blob_name=destination_blob_name)

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


sftp = establish_sftp_connection()

exit(0)
