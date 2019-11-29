import os
import pysftp
import pybase64
import hashlib
from google.cloud import storage


def main():
    # Config details
    survey_destination_path = 'OPN/opn1911a/'
    survey_source_path = 'ONS/' + survey_destination_path
    bucket_name = 'nisra-transfer'
    file_list = ['opn1911a.manifest']
    bucket = connect_to_bucket(bucket_name)

    try:
        print('Attempting sftp connection...')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:
            print('Connection established.')

            for file in file_list:

                print('Copying {} from SFTP server to container storage.'.format(file))
                sftp.get(survey_source_path + file, file)

                blob_destination_path = survey_destination_path + file
                file_blob = bucket.get_blob(blob_destination_path)

                if file_blob is None:
                    print('Uploading {} to bucket {}'.format(file, bucket_name))
                    upload_blob(bucket_name=bucket_name,
                                source_file_name=file,
                                destination_blob_name=blob_destination_path)
                elif file_same_as_bucket_file(file, file_blob):
                    print('Ignoring file {} because it has not changed'.format(file))
                else:
                    print('Uploading {} to bucket {}'.format(file, bucket_name))
                    upload_blob(bucket_name=bucket_name,
                                source_file_name=file,
                                destination_blob_name=blob_destination_path)
    except Exception as err:
        print('Connection error:', err)
        raise

    return


def file_same_as_bucket_file(file, file_blob):
    """Compares a file and a blob using md5."""

    file_blob_md5 = pybase64.b64decode(file_blob.md5_hash)
    print('MD5 of {} in bucket is {} '.format(file_blob.name, file_blob_md5))

    with open(file) as file_to_check:
        data = file_to_check.read()
        file_md5 = hashlib.md5(data.encode('utf-8')).digest()
        print('MD5 of {} is {} '.format(file, file_md5))

    if file_blob_md5 == file_md5:
        same_file = True
        print('File {} and blob {} are the same'.format(file, file_blob.name))
    else:
        same_file = False
        print('File {} and blob {} are different'.format(file, file_blob.name))

    return same_file


def connect_to_bucket(bucket_name):

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    return bucket


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket. Replaces already existing blob"""
    bucket = connect_to_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

    return


if __name__ == "__main__":
    main()

