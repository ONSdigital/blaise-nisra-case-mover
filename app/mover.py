from copy import deepcopy
from typing import Dict

import pysftp
from flask import Blueprint, current_app, request
from paramiko import SSHException

from models import Instrument, ProcessorEvent
from pkg.config import Config
from pkg.google_storage import init_google_storage
from pkg.sftp import SFTP
from util.service_logging import log

mover = Blueprint("batch", __name__, url_prefix="/")


@mover.route("/")
def main():
    survey_source_path = request.args.get("survey_source_path")
    config = deepcopy(current_app.nisra_config)
    sftp_config = deepcopy(current_app.sftp_config)
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
        instruments = get_filtered_instruments(sftp)
        log.info(f"Processing survey - {sftp_config.survey_source_path}")

        if len(instruments) == 0:
            log.info("No instrument folders found")
            return "No instrument folders found, exiting", 200

        for instrument_name, instrument in instruments.items():
            trigger_processor(
                config,
                ProcessorEvent(instrument_name=instrument_name, instrument=instrument),
            )

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


def trigger_processor(config: Config, processor_event: ProcessorEvent) -> None:
    log.info(f"Triggering processor for: {processor_event.instrument_name}")
    topic_path = current_app.publisher_client.topic_path(
        config.project_id, config.processor_topic_name
    )
    msg_bytes = bytes(processor_event.json(), encoding="utf-8")
    current_app.publisher_client.publish(topic_path, data=msg_bytes)
    log.info(f"Queued on pubsub for: {processor_event.instrument_name}")


def get_filtered_instruments(sftp: SFTP) -> Dict[str, Instrument]:
    instrumets = sftp.get_instrument_folders()
    instruments = sftp.get_instrument_files(instrumets)
    instruments = sftp.filter_instrument_files(instruments)
    instruments = sftp.generate_bdbx_md5s(instruments)
    return instruments
