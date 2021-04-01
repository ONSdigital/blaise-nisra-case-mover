import pysftp
from case_mover import CaseMover
from config import Config
from google_storage import GoogleStorage
from sftp import SFTP, SFTPConfig

from util.service_logging import log

sftp_config = SFTPConfig.from_env()
print(sftp_config)
config = Config()

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

with pysftp.Connection(
    host=sftp_config.host,
    username=sftp_config.username,
    password=sftp_config.password,
    port=int(sftp_config.port),
    cnopts=cnopts,
) as sftp_connection:
    sftp = SFTP(sftp_connection, sftp_config, config)
    instrumets = sftp.get_instrument_folders()
    instruments = sftp.get_instrument_files(instrumets)
    instruments = sftp.filter_instrument_files(instruments)
    instruments = sftp.generate_bdbx_md5s(instruments)
    print(instruments)

    google_storage = GoogleStorage(config.bucket_name, log)
    google_storage.initialise_bucket_connection()

    case_mover = CaseMover(google_storage, config, sftp)
    for instrument_name, instrument in instruments.items():
        print(f"Syncing instrument '{instrument_name}'")
        if not case_mover.compare_bdbx_md5(instrument):
            case_mover.sync_instrument(instrument)
            case_mover.send_request_to_api(instrument.gcp_folder())
