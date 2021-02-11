import fnmatch
import hashlib
import json
import re

import pybase64
import pysftp
import requests
from flask import Flask
from paramiko import SSHException

from config import *
from google_storage import GoogleStorage
from util.service_logging import log

app = Flask(__name__)

googleStorage = GoogleStorage(bucket_name, log)


@app.route("/")
def main():
    log.info("Application started")
    log.info(f"survey_source_path - {survey_source_path}")
    log.info(f"bucket_name - {bucket_name}")
    log.info(f"instrument_regex - {instrument_regex}")
    log.info(f"extension_list - {str(extension_list)}")
    log.info(f"sftp_host - {sftp_host}")
    log.info(f"sftp_port - {sftp_port}")
    log.info(f"sftp_username - {sftp_username}")
    log.info(f"server_park - {os.getenv('SERVER_PARK', 'env_var_not_set')}")
    log.info(f"blaise_api_url - {os.getenv('BLAISE_API_URL', 'env_var_not_set')}")

    googleStorage.initialise_bucket_connection()
    if googleStorage.bucket is None:
        return "Connection to bucket failed", 500

    try:
        log.info("Connecting to SFTP server")
        # cnopts = pysftp.CnOpts()
        # cnopts.hostkeys = None

        with pysftp.Connection(
            host=sftp_host,
            username=sftp_username,
            password=sftp_password,
            port=int(sftp_port)
        ) as sftp:
            log.info("Connected to SFTP server")

            if survey_source_path == "":
                log.exception("survey_source_path is blank")
                sftp.close()
                return "survey_source_path is blank, exiting", 500

            log.info("Processing survey - " + survey_source_path)
            instrument_folders = get_instrument_folders(sftp, survey_source_path)
            if len(instrument_folders) == 0:
                log.info("No instrument folders found")
                return "No instrument folders found, exiting", 200
            for instrument_folder in instrument_folders:
                process_instrument(sftp, f"{survey_source_path}{instrument_folder}/")

        sftp.close()
        log.info("SFTP connection closed")
        log.info("Process complete")
        return "Process complete", 200

    except SSHException:
        log.error("SFTP connection failed")
        return "SFTP connection failed", 500
    except Exception as ex:
        log.error("Exception - %s", ex)
        sftp.close()
        log.info("SFTP connection closed")
        return "Exception occurred", 500


def get_instrument_folders(sftp, source_path):
    survey_folder_list = []
    for folder in sftp.listdir(source_path):
        if re.compile(instrument_regex).match(folder):
            log.info(f"Instrument folder found - {folder}")
            survey_folder_list.append(folder)
    return survey_folder_list


def process_instrument(sftp, source_path):
    instrument_name = source_path[-9:].strip("/")
    instrument_db_file = f"{instrument_name}.bdbx"
    log.info(f"Processing instrument - {instrument_name}")
    delete_local_instrument_files()
    instrument_files = get_instrument_files(sftp, source_path)
    if len(instrument_files) == 0:
        log.info(f"No instrument files found in folder - {source_path}")
        return f"No instrument files found in folder - {source_path}"
    if not check_instrument_database_file_exists(instrument_files, instrument_name):
        log.info(f"Instrument database file not found - {instrument_db_file}")
        return f"Instrument database file not found - {instrument_db_file}"
    sftp.get(source_path + instrument_db_file, instrument_db_file)
    log.info("Checking if database file has already been processed...")
    if not check_if_matching_file_in_bucket(
        instrument_db_file, f"{instrument_name}/{instrument_db_file}"
    ):
        upload_instrument(sftp, source_path, instrument_name, instrument_files)


def check_instrument_database_file_exists(instrument_files, instrument_name):
    if not instrument_files:
        return False
    for instrument_file in instrument_files:
        if instrument_file.lower() == instrument_name.lower() + ".bdbx":
            log.info(f"Database file found - {instrument_file}")
            return True
    return False


def delete_local_instrument_files():
    files = [file for file in os.listdir(".") if os.path.isfile(file)]
    for file in files:
        if any(fnmatch.fnmatch(file, pattern) for pattern in extension_list):
            log.info(f"Deleting local instrument file - {file}")
            os.remove(file)


def get_instrument_files(sftp, source_path):
    instrument_file_list = []
    for instrument_file in sftp.listdir(source_path):
        if any(fnmatch.fnmatch(instrument_file, pattern) for pattern in extension_list):
            log.info(f"Instrument file found - {instrument_file}")
            instrument_file_list.append(instrument_file)
    return instrument_file_list


def check_if_matching_file_in_bucket(local_file, bucket_file_location):
    bucket_file = googleStorage.get_blob(bucket_file_location)
    if bucket_file is None:
        log.info(f"File {bucket_file} not found in bucket")
        return False

    try:
        with open(local_file, "rb") as local_file_to_check:
            local_file_data = local_file_to_check.read()
            local_file_md5 = hashlib.md5(local_file_data).digest()
            log.info(f"MD5 for Local file - {local_file} = {str(local_file_md5)}")
    except (OSError, IOError) as e:
        log.error(e, f"Failed to read local file - {local_file}")

    bucket_file_md5 = pybase64.b64decode(bucket_file.md5_hash)
    log.info(f"MD5 for Bucket file - {bucket_file.name} = {bucket_file_md5}")

    if local_file_md5 == bucket_file_md5:
        log.info(f"Files {local_file} and {bucket_file.name} match")
        return True
    else:
        log.info(f"Files do not match - {local_file} - {bucket_file.name}")
        return False


def upload_instrument(sftp, source_path, instrument_name, instrument_files):
    log.info(f"Uploading instrument - {instrument_name}")
    for instrument_file in instrument_files:
        log.info(f"Downloading instrument file from SFTP - {instrument_file}")
        sftp.get(source_path + instrument_file, instrument_file)
        log.info(
            f"Uploading instrument file to bucket - {instrument_name}/{instrument_file}"
        )
        googleStorage.upload_file(
            instrument_file, f"{instrument_name}/{instrument_file}"
        )
    send_request_to_api(instrument_name)


def send_request_to_api(instrument_name):
    server_park = os.getenv("SERVER_PARK", "env_var_not_set")
    blaise_api_url = os.getenv("BLAISE_API_URL", "env_var_not_set")
    data = {"InstrumentDataPath": instrument_name}
    log.info(f"Sending request to {blaise_api_url} for instrument {instrument_name}")
    request = requests.post(
        f"http://{blaise_api_url}/api/vi/serverparks/{server_park}/instruments/{instrument_name}/data",
        headers={"content-type": "application/json"},
        data=json.dumps(data),
    )
    log.info(f"Status code response from {blaise_api_url} - {request.status_code}")
