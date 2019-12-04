import os
import pysftp
import pybase64
import hashlib
import fnmatch
from config import survey_source_path, survey_destination_path
from config import bucket_name, extension_list
from google.cloud import storage
from util.service_logging import log


def main():

    bucket = connect_to_bucket()
    processed_folder = 'processed/'

    try:
        log.info('Attempting SFTP connection...')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:

            log.info('SFTP connection established.')

            if not processed_folder_exists(folder_name=processed_folder):
                os.mknod(processed_folder)
                log.info('Creating empty processed folder for {}.'.format(survey_destination_path))
                upload_blob(source_file_name='processed',
                            destination_blob_name=survey_destination_path + 'processed/')

            file_list = list_files_to_transfer(sftp)

            for file in file_list:

                blob_destination_path = survey_destination_path + file

                file_blob = bucket.get_blob(blob_destination_path)

                log.info('Copying {} from SFTP server to container storage.'.format(file))
                sftp.get(survey_source_path + file, file)

                if file_blob is None:
                    upload_blob(source_file_name=file,
                                destination_blob_name=blob_destination_path)
                elif file_same_as_bucket_file(file, file_blob):
                    log.info('Ignoring file {} because its unchanged'.format(file))
                else:
                    upload_blob(source_file_name=file,
                                destination_blob_name=blob_destination_path)
    except Exception as err:
        log.error('Connection error:', err)
        raise

    return 0


def processed_folder_exists(folder_name):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=survey_destination_path)

    blob_names = [blob.name for blob in blobs]

    folder_in_blobs = [True for blob in blob_names if folder_name in blob]

    if any(folder_in_blobs):
        log.info('Processed folder exists for {}'.format(survey_destination_path))
        return True
    else:
        log.info('Processed folder for {} does not exist'.format(survey_destination_path))
        return False


def list_files_to_transfer(sftp):
    file_list = []

    for filename in sftp.listdir(survey_source_path):
        if any(fnmatch.fnmatch(filename, pattern) for pattern in extension_list):
            file_list.append(filename)

    log.info('Available files on SFTP server: '.format(file_list))

    return file_list


def file_same_as_bucket_file(file, file_blob):
    """Compares a file and a blob using md5."""

    log.info('Comparing file {} to blob {}.'.format(file, file_blob.name))

    file_blob_md5 = pybase64.b64decode(file_blob.md5_hash)
    log.debug('MD5 of {} in bucket is {}.'.format(file_blob.name, file_blob_md5))

    with open(file, 'rb') as file_to_check:
        data = file_to_check.read()
        file_md5 = hashlib.md5(data).digest()
        log.debug('MD5 of {} is {}.'.format(file, file_md5))

    if file_blob_md5 == file_md5:
        same_file = True
        log.info('File {} and blob {} are the same.'.format(file, file_blob.name))
    else:
        same_file = False
        log.info('File {} and blob {} are different.'.format(file, file_blob.name))

    return same_file


def connect_to_bucket():
    """ Connects to storage client and gets the bucket """

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    return bucket


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket. Replaces already existing blob"""

    bucket = connect_to_bucket()
    blob = bucket.blob(destination_blob_name)

    log.info('Uploading file {} to bucket {}'.format(source_file_name, bucket_name))
    blob.upload_from_filename(source_file_name)
    log.info('File {} successfully uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

    return


if __name__ == "__main__":
    main()

