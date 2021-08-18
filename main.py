import base64

import pysftp
from google.cloud import pubsub_v1

from models.processor_event import ProcessorEvent
from models.trigger_event import TriggerEvent
from pkg.case_mover import CaseMover
from pkg.config import Config
from pkg.google_storage import init_google_storage
from pkg.sftp import SFTP, SFTPConfig
from pkg.trigger import get_filtered_instruments, trigger_processor
from processor import process_instrument
from util.service_logging import log


def trigger(event, _context):
    trigger_event = TriggerEvent.from_json(
        base64.b64decode(event["data"]).decode("utf-8")
    )
    print(f"Nisra triggered for survey: '{trigger_event.survey}'")
    config = Config.from_env()
    sftp_config = SFTPConfig.from_env()
    config.log()
    sftp_config.survey_source_path = trigger_event.survey
    sftp_config.log()
    publisher_client = pubsub_v1.PublisherClient()

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    cnopts.compression = True

    google_storage = init_google_storage(config)
    if google_storage.bucket is None:
        return "Connection to bucket failed", 500

    log.info("Connecting to SFTP server")

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
        instruments = get_filtered_instruments(sftp, case_mover)
        log.info(f"Processing survey - {sftp_config.survey_source_path}")

        if len(instruments) == 0:
            log.info("No instrument folders found after filtering")
            return "No instrument folders found, exiting", 200

        for instrument_name, instrument in instruments.items():
            trigger_processor(
                publisher_client,
                config,
                ProcessorEvent(instrument_name=instrument_name, instrument=instrument),
            )


def processor(event, _context):
    config = Config.from_env()
    sftp_config = SFTPConfig.from_env()
    config.log()
    sftp_config.log()

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    cnopts.compression = True

    google_storage = init_google_storage(config)
    if google_storage.bucket is None:
        return "Connection to bucket failed", 500

    log.info("Connecting to SFTP server")

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

        processor_event = ProcessorEvent.from_json(
            base64.b64decode(event["data"]).decode("utf-8")
        )

        process_instrument(
            case_mover, processor_event.instrument_name, processor_event.instrument
        )
