import fnmatch
import hashlib
import re

import pybase64
import pysftp
from google.cloud import storage

from config import *
from util.service_logging import log


def main():
    log.info('Application started')
    log.info('instrument_source_path - ' + instrument_source_path)
    log.info('survey_source_path - ' + survey_source_path)
    log.info('instrument_destination_path - ' + instrument_destination_path)
    log.info('bucket_name - ' + bucket_name)
    log.info('instrument_regex - ' + instrument_regex)
    log.info('extension_list - ' + str(extension_list))

    try:
        log.info('Connecting to SFTP server')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:
            log.info('Connected to SFTP server')

            if survey_source_path != '':
                log.info('Processing survey - ' + survey_source_path)
                instrument_folders = get_instrument_folders(sftp, survey_source_path)
                for instrument_folder in instrument_folders:
                    delete_local_instrument_files()
                    create_processed_folder(instrument_destination_path + instrument_folder + '/')
                    instrument_files = get_instrument_files(sftp, survey_source_path + instrument_folder + '/')
                    process_instrument_files(sftp, survey_source_path + instrument_folder + '/', instrument_files,
                                             instrument_destination_path + instrument_folder + '/')

            if instrument_source_path != '':
                log.info('Processing instrument - ' + instrument_source_path)
                delete_local_instrument_files()
                create_processed_folder(instrument_destination_path + instrument_source_path[-9:])
                instrument_files = get_instrument_files(sftp, survey_source_path + instrument_source_path[-9:])
                process_instrument_files(sftp, survey_source_path + instrument_source_path[-9:], instrument_files,
                                         instrument_destination_path + instrument_source_path[-9:])

        log.info('SFTP connection closed')

    except Exception as ex:
        log.info('SFTP connection closed')
        log.error('Exception - %s', ex)
        raise


def get_instrument_folders(sftp, survey_source_path):
    survey_folder_list = []
    for folder in sftp.listdir(survey_source_path):
        if re.compile(instrument_regex).match(folder):
            log.info('Instrument folder found - ' + folder)
            survey_folder_list.append(folder)
    return survey_folder_list


def create_processed_folder(instrument_destination):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=instrument_destination)
    blob_names = [blob.name for blob in blobs]
    processed_folder_found = False
    for blob_name in blob_names:
        if blob_name == instrument_destination + 'processed/':
            log.info('Processed folder already exists for ' + instrument_destination)
            processed_folder_found = True
    if not processed_folder_found:
        log.info('Creating processed folder for ' + instrument_destination)
        open('processed', 'w').close()
        upload_file('processed', instrument_destination + 'processed/')


def get_instrument_files(sftp, source_instrument_path):
    instrument_file_list = []
    for instrument_file in sftp.listdir(source_instrument_path):
        if any(fnmatch.fnmatch(instrument_file, pattern) for pattern in extension_list):
            log.info('Instrument file found - ' + instrument_file)
            instrument_file_list.append(instrument_file)
    return instrument_file_list


def process_instrument_files(sftp, source_instrument_path, instrument_files, destination_path):
    for instrument_file in instrument_files:
        destination_blob = destination_path + instrument_file
        bucket = connect_to_bucket()
        instrument_file_blob = bucket.get_blob(destination_blob)
        instrument_file_blob_processed = bucket.get_blob(destination_path + 'processed/' + instrument_file)
        log.info('Downloading instrument file locally - ' + instrument_file)
        sftp.get(source_instrument_path + instrument_file, instrument_file)
        log.info('Processing instrument file - ' + instrument_file)
        if instrument_file_blob is None and instrument_file_blob_processed is None:
            upload_file(instrument_file, destination_blob)
        elif instrument_file_blob is None and instrument_file_blob_processed is not None:
            if check_if_files_match(instrument_file, instrument_file_blob_processed) is False:
                upload_file(instrument_file, destination_blob)
        elif instrument_file_blob is not None and instrument_file_blob_processed is None:
            if check_if_files_match(instrument_file, instrument_file_blob) is False:
                upload_file(instrument_file, destination_blob)
        elif instrument_file_blob is not None and instrument_file_blob_processed is not None:
            if check_if_files_match(instrument_file, instrument_file_blob) is False:
                upload_file(instrument_file, destination_blob)


def upload_file(source, destination):
    bucket = connect_to_bucket()
    blob_destination = bucket.blob(destination)
    log.info('Uploading file - ' + source)
    blob_destination.upload_from_filename(source)
    log.info('Uploaded file - ' + source)


def check_if_files_match(local_file, bucket_file):
    with open(local_file, 'rb') as local_file_to_check:
        local_file_data = local_file_to_check.read()
        local_file_md5 = hashlib.md5(local_file_data).digest()
        log.info('Local file MD5 - ' + local_file + ' - ' + str(local_file_md5))
    bucket_file_md5 = pybase64.b64decode(bucket_file.md5_hash)
    log.info('Bucket file MD5 - ' + bucket_file.name + ' - ' + str(bucket_file_md5))
    if local_file_md5 == bucket_file_md5:
        log.info('Files match - ' + local_file + ' - ' + bucket_file.name)
        return True
    else:
        log.info('Files do not match - ' + local_file + ' - ' + bucket_file.name)
        return False


def connect_to_bucket():
    try:
        log.info('Connecting to bucket - ' + bucket_name)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        log.info('Connected to bucket - ' + bucket_name)
        return bucket
    except Exception as ex:
        log.error('Exception - %s', ex)
        raise


def delete_local_instrument_files():
    files = [file for file in os.listdir('.') if os.path.isfile(file)]
    for file in files:
        if any(fnmatch.fnmatch(file, pattern) for pattern in extension_list):
            log.info("Deleting local instrument file - " + file)
            os.remove(file)


if __name__ == "__main__":
    main()
