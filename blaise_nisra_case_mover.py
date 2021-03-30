import fnmatch
import hashlib
import json
import os
import re

import pybase64
import pysftp
import requests
from flask import Flask
from paramiko import SSHException

from config import Config, SFTPConfig
from google_storage import GoogleStorage
from util.service_logging import log

app = Flask(__name__)


@app.route("/")
def main():

    sftp_config = SFTPConfig()
    config = Config()
    log.info("Application started")
    log.info(f"survey_source_path - {sftp_config.survey_source_path}")
    log.info(f"bucket_name - {config.bucket_name}")
    log.info(f"instrument_regex - {config.instrument_regex}")
    log.info(f"extension_list - {str(config.extension_list)}")
    log.info(f"sftp_host - {sftp_config.host}")
    log.info(f"sftp_port - {sftp_config.port}")
    log.info(f"sftp_username - {sftp_config.username}")
    log.info(f"server_park - {config.server_park}")
    log.info(f"blaise_api_url - {config.blaise_api_url}")

    google_storage = GoogleStorage(config.bucket_name, log)
    google_storage.initialise_bucket_connection()
    if google_storage.bucket is None:
        return "Connection to bucket failed", 500

    try:
        log.info("Connecting to SFTP server")
        # cnopts = pysftp.CnOpts()
        # cnopts.hostkeys = None

        with pysftp.Connection(
            host=sftp_config.host,
            username=sftp_config.username,
            password=sftp_config.password,
            port=int(sftp_config.port),
        ) as sftp:
            log.info("Connected to SFTP server")

            if sftp_config.survey_source_path == "":
                log.exception("survey_source_path is blank")
                sftp.close()
                return "survey_source_path is blank, exiting", 500

            log.info("Processing survey - " + sftp_config.survey_source_path)
            instrument_folders = get_instrument_folders(sftp, sftp_config, config)
            if len(instrument_folders) == 0:
                log.info("No instrument folders found")
                return "No instrument folders found, exiting", 200
            for instrument_folder in instrument_folders:
                process_instrument(
                    sftp,
                    f"{sftp_config.survey_source_path}{instrument_folder}/",
                    config,
                )

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


def get_instrument_folders(sftp, sftp_config, config):
    survey_folder_list = []
    for folder in sftp.listdir(sftp_config.survey_source_path):
        if re.compile(config.instrument_regex).match(folder):
            log.info(f"Instrument folder found - {folder}")
            survey_folder_list.append(folder)
    return survey_folder_list


def process_instrument(sftp, google_storage, source_path, config):
    instrument_name = source_path[-9:].strip("/")
    instrument_db_file = f"{instrument_name}.bdbx"
    log.info(f"Processing instrument - {instrument_name}")
    delete_local_instrument_files(config)
    instrument_files = get_instrument_files(sftp, source_path, config)
    if len(instrument_files) == 0:
        log.info(f"No instrument files found in folder - {source_path}")
        return f"No instrument files found in folder - {source_path}"
    if not check_instrument_database_file_exists(instrument_files, instrument_name):
        log.info(f"Instrument database file not found - {instrument_db_file}")
        return f"Instrument database file not found - {instrument_db_file}"
    instrument_db_file = get_actual_instrument_database_file_name(
        instrument_files, instrument_name
    )
    sftp.get(source_path + instrument_db_file, instrument_db_file)
    log.info("Checking if database file has already been processed...")
    if not check_if_matching_file_in_bucket(
        google_storage,
        instrument_db_file,
        f"{instrument_name}/{instrument_db_file}".upper(),
    ):
        upload_instrument(sftp, source_path, instrument_name, instrument_files)
        send_request_to_api(instrument_name.upper())


def check_instrument_database_file_exists(instrument_files, instrument_name):
    if not instrument_files:
        return False
    for instrument_file in instrument_files:
        if instrument_file.lower() == instrument_name.lower() + ".bdbx":
            log.info(f"Database file found - {instrument_file}")
            return True
    return False


def get_actual_instrument_database_file_name(instrument_files, instrument_name):
    if not instrument_files:
        return False
    for instrument_file in instrument_files:
        if instrument_file.lower() == instrument_name.lower() + ".bdbx":
            return instrument_file
    return False


def delete_local_instrument_files(config):
    files = [file for file in os.listdir(".") if os.path.isfile(file)]
    for file in files:
        if any(fnmatch.fnmatch(file, pattern) for pattern in config.extension_list):
            log.info(f"Deleting local instrument file - {file}")
            os.remove(file)


def get_instrument_files(sftp, source_path, config):
    instrument_file_list = []
    for instrument_file in sftp.listdir(source_path):
        if any(
            fnmatch.fnmatch(instrument_file.lower(), pattern)
            for pattern in config.extension_list
        ):
            log.info(f"Instrument file found - {instrument_file}")
            instrument_file_list.append(instrument_file)
    return instrument_file_list


def check_if_matching_file_in_bucket(google_storage, local_file, bucket_file_location):
    bucket_file = google_storage.get_blob(bucket_file_location)
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


def upload_instrument(
    sftp, google_storage, source_path, instrument_name, instrument_files
):
    log.info(f"Uploading instrument - {instrument_name}")
    for instrument_file in instrument_files:
        log.info(f"Downloading instrument file from SFTP - {instrument_file}")
        sftp.get(source_path + instrument_file, instrument_file)
        log.info(
            f"Uploading instrument file to bucket - {instrument_name}/{instrument_file}"
        )
        google_storage.upload_file(
            instrument_file, f"{instrument_name}/{instrument_file}".upper()
        )


def send_request_to_api(instrument_name, config):
    # added 10 second timeout exception pass to the api request because the connection to the api was timing out
    # before it completed the work. this also allows parallel requests to be made to the api.

    data = {"instrumentDataPath": instrument_name}
    log.info(
        f"Sending request to {config.blaise_api_url} for instrument {instrument_name}"
    )
    try:
        requests.post(
            f"http://{config.blaise_api_url}/api/v1/serverparks/{config.server_park}/instruments/{instrument_name}/data",
            headers={"content-type": "application/json"},
            data=json.dumps(data),
            timeout=10,
        )
    except requests.exceptions.ReadTimeout:
        pass
