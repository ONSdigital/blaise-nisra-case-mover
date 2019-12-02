import os
import pysftp
import pybase64
import hashlib
import glob
from config import survey_source_path, survey_destination_path
from config import bucket_name, extension_list
from google.cloud import storage


def main():

    bucket = connect_to_bucket()

    # Grab files names based on extensions
    file_list = []
    for ext in extension_list:
        file_list.extend(glob.glob(ext))

    try:
        print('Attempting SFTP connection...')
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
                    upload_blob(source_file_name=file,
                                destination_blob_name=blob_destination_path)
                elif file_same_as_bucket_file(file, file_blob):
                    print('Ignoring file {} because its unchanged'.format(file))
                else:
                    print('Uploading file {} to bucket {}'.format(file, bucket_name))
                    upload_blob(source_file_name=file,
                                destination_blob_name=blob_destination_path)
    except Exception as err:
        print('Connection error:', err)
        raise

    return 0


def file_same_as_bucket_file(file, file_blob):
    """Compares a file and a blob using md5."""

    print('Comparing file {} to blob {}.'.format(file, file_blob.name))

    file_blob_md5 = pybase64.b64decode(file_blob.md5_hash)
    print('MD5 of {} in bucket is {}.'.format(file_blob.name, file_blob_md5))

    with open(file, 'rb') as file_to_check:
        data = file_to_check.read()
        file_md5 = hashlib.md5(data).digest()
        print('MD5 of {} is {}.'.format(file, file_md5))

    if file_blob_md5 == file_md5:
        same_file = True
        print('File {} and blob {} are the same.'.format(file, file_blob.name))
    else:
        same_file = False
        print('File {} and blob {} are different.'.format(file, file_blob.name))

    return same_file


def connect_to_bucket():

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    return bucket


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket. Replaces already existing blob"""
    bucket = connect_to_bucket()
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

    return


if __name__ == "__main__":
    main()

