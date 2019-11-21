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
            sftp.get('ONS/OPN/opn1911a/OPN1911a.manifest', 'tmp/OPN1911a.manifest')

            bucket_name = 'nisra-transfer'
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob('tmp')
            blob.upload_from_filename('OPN1911a.manifest')
    except Exception as err:
        print('Connection error:', err)
        raise

    return sftp


sftp = establish_sftp_connection()

exit(0)
