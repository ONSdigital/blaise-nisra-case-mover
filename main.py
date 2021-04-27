import os
from app.app import app, load_config

if __name__ == "__main__":
    load_config(app)
    port = os.getenv("5000")
    app.run(host="0.0.0.0", port=port)

import base64

import pysftp

from models.processor_event import ProcessorEvent
from pkg.case_mover import CaseMover
from pkg.config import Config
from pkg.google_storage import init_google_storage
from pkg.sftp import SFTP, SFTPConfig
from processor import process_instrument
from util.service_logging import log


def processor(event, _context):
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
