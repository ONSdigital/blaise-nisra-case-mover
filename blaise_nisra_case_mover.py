import fnmatch
import hashlib
import json
import re
import pybase64
import pysftp
import requests
from paramiko import SSHException

from config import *
from util.service_logging import log
from flask import Flask
from GoogleStorage import GoogleStorage

app = Flask(__name__)

googleStorage = GoogleStorage(bucket_name, log)


@app.route('/')
def main():
    log.info('Application started')
    log.info('survey_source_path - ' + survey_source_path)
    log.info('bucket_name - ' + bucket_name)
    log.info('instrument_regex - ' + instrument_regex)
    log.info('extension_list - ' + str(extension_list))
    log.info('sftp_host - ' + SFTP_HOST)
    log.info('sftp_port - ' + SFTP_PORT)
    log.info('sftp_username - ' + SFTP_USERNAME)

    googleStorage.initialise_bucket_connection()
    if googleStorage.bucket is None:
        return 'Connection to bucket failed', 500

    try:
        log.info('Connecting to SFTP server')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(host=SFTP_HOST,
                               username=SFTP_USERNAME,
                               password=SFTP_PASSWORD,
                               port=int(SFTP_PORT),
                               cnopts=cnopts) as sftp:
            log.info('Connected to SFTP server')

            if survey_source_path == '':
                log.exception('survey_source_path is blank')
                sftp.close()
                return "survey_source_path is blank, exiting", 500

            log.info('Processing survey - ' + survey_source_path)
            instrument_folders = get_instrument_folders(sftp, survey_source_path)
            if len(instrument_folders) == 0:
                log.info("No instrument folders found")
                return "No instrument folders found, exiting", 200
            for instrument_folder in instrument_folders:
                process_instrument(sftp, survey_source_path + instrument_folder + '/')

        sftp.close()
        log.info('SFTP connection closed')
        log.info('Process Complete')
        return "Process Complete", 200

    except SSHException:
        log.error('SFTP connection failed')
        return "SFTP connection failed", 500
    except Exception as ex:
        log.error('Exception - %s', ex)
        sftp.close()
        log.info('SFTP connection closed')
        return "Exception occurred", 500


def get_instrument_folders(sftp, source_path):
    survey_folder_list = []
    for folder in sftp.listdir(source_path):
        if re.compile(instrument_regex).match(folder):
            log.info('Instrument folder found - ' + folder)
            survey_folder_list.append(folder)
    return survey_folder_list


def process_instrument(sftp, source_path):
    instrument_name = source_path[-9:]
    log.info('Processing instrument - ' + instrument_name)
    delete_local_instrument_files()
    instrument_files = get_instrument_files(sftp, source_path)
    if len(instrument_files) == 0:
        log.info(f"No instrument files found in folder: {instrument_name}")
        return f"No instrument files found in folder: {instrument_name}"
    for instrument_file in instrument_files:
        if not instrument_file.lower().endswith('bdbx'):
            continue

        log.info('Database file found - ' + instrument_file)
        sftp.get(source_path + instrument_file, instrument_file)
        log.info('Checking if database file has already been processed...')
        if not check_if_matching_file_in_bucket(instrument_file, instrument_name + instrument_file):
            upload_instrument(sftp, source_path, instrument_name, instrument_files)


def delete_local_instrument_files():
    files = [file for file in os.listdir('.') if os.path.isfile(file)]
    for file in files:
        if any(fnmatch.fnmatch(file, pattern) for pattern in extension_list):
            log.info("Deleting local instrument file - " + file)
            os.remove(file)


def get_instrument_files(sftp, source_path):
    instrument_file_list = []
    for instrument_file in sftp.listdir(source_path):
        if any(fnmatch.fnmatch(instrument_file, pattern) for pattern in extension_list):
            log.info('Instrument file found - ' + instrument_file)
            instrument_file_list.append(instrument_file)
    return instrument_file_list


def check_if_matching_file_in_bucket(local_file, bucket_file_location):
    bucket_file = googleStorage.get_blob(bucket_file_location)
    if bucket_file is None:
        log.info(f'File {bucket_file} not found in bucket')
        return False

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


def upload_instrument(sftp, source_path, instrument_name, instrument_files):
    log.info('Uploading instrument - ' + instrument_name)
    for instrument_file in instrument_files:
        log.info('Downloading instrument file from SFTP - ' + instrument_file)
        sftp.get(source_path + instrument_file, instrument_file)
        log.info('Uploading instrument file to bucket - ' + instrument_name + instrument_file)
        googleStorage.upload_file(instrument_file, instrument_name + instrument_file)

    send_request_to_API(instrument_name)


def send_request_to_API(instrument_name):
    data = {"InstrumentDataPath": instrument_name}
    log.info(f'Sending request to BLAISE_API_URL for {instrument_name}')
    request = requests.post(
        f"http://{BLAISE_API_URL}/api/vi/serverpark/{SERVER_PARK}/instruments/{instrument_name}data",
        headers={"content-type": "application/json"},
        data=json.dumps(data),
    )
    log.info(f'Response from BLAISE_API_URL status code: {request.status_code}')


@app.errorhandler(500)
def internal_error(error):
    log.exception("Exception occurred", error)
    return "Exception occurred", 500
