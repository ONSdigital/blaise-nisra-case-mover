import pysftp
from flask import Flask
from paramiko import SSHException

from case_mover import CaseMover
from config import Config, SFTPConfig
from google_storage import GoogleStorage
from models import Instrument
from sftp import SFTP
from util.service_logging import log

app = Flask(__name__)


@app.route("/")
def main():

    sftp_config = SFTPConfig.from_env()
    config = Config.from_env()
    log.info("Application started")
    config.log()
    sftp_config.log()

    google_storage = GoogleStorage(config.bucket_name, log)
    google_storage.initialise_bucket_connection()
    if google_storage.bucket is None:
        return "Connection to bucket failed", 500

    try:
        log.info("Connecting to SFTP server")
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(
            host=sftp_config.host,
            username=sftp_config.username,
            password=sftp_config.password,
            port=int(sftp_config.port),
            cnopts=cnopts,
        ) as sftp_connection:
            log.info("Connected to SFTP server")

            if sftp_config.survey_source_path == "":
                log.exception("survey_source_path is blank")
                return "survey_source_path is blank, exiting", 500

            sftp = SFTP(sftp_connection, sftp_config, config)
            instruments = get_filtered_instruments(sftp)
            case_mover = CaseMover(google_storage, config, sftp)
            log.info(f"Processing survey - {sftp_config.survey_source_path}")
            if len(instruments) == 0:
                log.info("No instrument folders found")
                return "No instrument folders found, exiting", 200
            for instrument_name, instrument in instruments.items():
                log.info(
                    f"Processing instrument - {instrument_name} - {instrument.sftp_path}"
                )
                if case_mover.compare_bdbx_md5(instrument):
                    log.info(
                        f"Instrument - {instrument_name} - has no changes to the databse file, skipping..."
                    )
                else:
                    log.info(f"Syncing instrument - {instrument_name}")
                    case_mover.sync_instrument(instrument)
                    case_mover.send_request_to_api(instrument.gcp_folder())
        log.info("SFTP connection closed")
        log.info("Process complete")
        return "Process complete", 200

    except SSHException:
        log.error("SFTP connection failed")
        return "SFTP connection failed", 500
    except Exception as ex:
        log.error("Exception - %s", ex)
        log.info("SFTP connection closed")
        return "Exception occurred", 500


def get_filtered_instruments(sftp: SFTP) -> Dict[str, Instrument]:
    instrumets = sftp.get_instrument_folders()
    instruments = sftp.get_instrument_files(instrumets)
    instruments = sftp.filter_instrument_files(instruments)
    instruments = sftp.generate_bdbx_md5s(instruments)
    return instruments
