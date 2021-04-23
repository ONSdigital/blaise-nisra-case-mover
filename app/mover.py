from typing import Dict

import pysftp
from flask import Blueprint, current_app, request
from paramiko import SSHException

from models import Instrument
from pkg.case_mover import CaseMover
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTP
from util.service_logging import log

mover = Blueprint("batch", __name__, url_prefix="/")


@mover.route("/")
def main():
    survey_source_path = request.args.get("survey_source_path")
    config = current_app.nisra_config
    sftp_config = current_app.sftp_config
    if survey_source_path:
        sftp_config.survey_source_path = survey_source_path
    google_storage = init_google_storage(config)
    if google_storage.bucket is None:
        return "Connection to bucket failed", 500

    log.info("Connecting to SFTP server")
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    cnopts.compression = True

    with pysftp.Connection(
        host=sftp_config.host,
        username=sftp_config.username,
        password=sftp_config.password,
        port=int(sftp_config.port),
        cnopts=cnopts,
    ) as sftp_connection:
        log.info("Connected to SFTP server")

        sftp = SFTP(sftp_connection, sftp_config, config)
        case_mover = CaseMover(google_storage, config, sftp)
        instruments = get_filtered_instruments(sftp)
        log.info(f"Processing survey - {sftp_config.survey_source_path}")

        if len(instruments) == 0:
            log.info("No instrument folders found")
            return "No instrument folders found, exiting", 200

        for instrument_name, instrument in instruments.items():
            process_instrument(case_mover, instrument_name, instrument)

    log.info("SFTP connection closed")
    log.info("Process complete")
    return "Process complete", 200


@mover.errorhandler(SSHException)
def handle_ssh_exception(exception):
    log.error("SFTP connection failed - %s", exception)
    return "SFTP connection failed", 500


@mover.errorhandler(Exception)
def handle_exception(exception):
    log.error("Exception - %s", exception)
    log.info("SFTP connection closed")
    return "Exception occurred", 500


def process_instrument(
    case_mover: CaseMover, instrument_name: str, instrument: Instrument
) -> None:
    log.info(f"Processing instrument - {instrument_name} - {instrument.sftp_path}")
    if case_mover.bdbx_md5_changed(instrument):
        log.info(
            f"Instrument - {instrument_name} - "
            + "has no changes to the databse file, skipping..."
        )
    else:
        log.info(f"Syncing instrument - {instrument_name}")
        case_mover.sync_instrument(instrument)
        case_mover.send_request_to_api(instrument.gcp_folder())


def get_filtered_instruments(sftp: SFTP) -> Dict[str, Instrument]:
    instrumets = sftp.get_instrument_folders()
    instruments = sftp.get_instrument_files(instrumets)
    instruments = sftp.filter_instrument_files(instruments)
    instruments = sftp.generate_bdbx_md5s(instruments)
    return instruments


def init_google_storage(config):
    google_storage = GoogleStorage(config.bucket_name, log)
    google_storage.initialise_bucket_connection()
    return google_storage
