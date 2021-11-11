from models import Instrument
from pkg.case_mover import CaseMover
import logging


def process_instrument(
    case_mover: CaseMover, instrument_name: str, instrument: Instrument
) -> None:
    logging.info(f"Processing instrument - {instrument_name} - {instrument.sftp_path}")
    if case_mover.instrument_needs_updating(instrument):
        log.info(f"Syncing instrument - {instrument_name}")
        case_mover.sync_instrument(instrument)
        case_mover.send_request_to_api(instrument.gcp_folder())
    else:
        logging.info(
            f"Instrument - {instrument_name} - "
            + "has no changes to the database file, skipping..."
        )
