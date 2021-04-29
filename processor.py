from models import Instrument
from pkg.case_mover import CaseMover
from util.service_logging import log


def process_instrument(
    case_mover: CaseMover, instrument_name: str, instrument: Instrument
) -> None:
    log.info(f"Processing instrument - {instrument_name} - {instrument.sftp_path}")
    if case_mover.instrument_needs_updating(instrument):
        log.info(f"Syncing instrument - {instrument_name}")
        case_mover.sync_instrument(instrument)
        case_mover.send_request_to_api(instrument.gcp_folder())
    else:
        log.info(
            f"Instrument - {instrument_name} - "
            + "has no changes to the database file, skipping..."
        )
