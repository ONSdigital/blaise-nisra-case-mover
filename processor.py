# Used for the processor cloud function

import base64

import pysftp

from models import Instrument
from models.processor_event import ProcessorEvent
from pkg.case_mover import CaseMover
from pkg.config import Config
from pkg.google_storage import init_google_storage
from pkg.sftp import SFTP, SFTPConfig
from util.service_logging import log


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


def main(event, _context):
    config = Config.from_env()
    sftp_config = SFTPConfig.from_env()

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    cnopts.compression = True

    google_storage = init_google_storage(config)
    if google_storage.bucket is None:
        return "Connection to bucket failed", 500

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
