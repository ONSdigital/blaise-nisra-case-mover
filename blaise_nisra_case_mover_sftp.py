import pysftp
from google.cloud import storage
import os


def establish_sftp_connection():
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        bucket_name = 'nisra-transfer'
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob('OPN1911a.bdbx')

        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:
            print(sftp.listdir('ONS/OPN/opn1911a'))
            blob.upload_from_filename(sftp.put('ONS/OPN/opn1911a/OPN1911a.bdbx'))

    except Exception as err:
        print('Connection error:', err)
        raise

    return sftp


sftp = establish_sftp_connection()

exit(0)
