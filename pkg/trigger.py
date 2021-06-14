from pkg.case_mover import CaseMover
from typing import Dict

from google.cloud import pubsub_v1

from models import Instrument, ProcessorEvent
from pkg.config import Config
from pkg.sftp import SFTP
from util.service_logging import log


def trigger_processor(
    publisher_client: pubsub_v1.PublisherClient,
    config: Config,
    processor_event: ProcessorEvent,
) -> None:
    log.info(f"Triggering processor for: {processor_event.instrument_name}")
    topic_path = publisher_client.topic_path(
        config.project_id, config.processor_topic_name
    )
    msg_bytes = bytes(processor_event.json(), encoding="utf-8")
    publisher_client.publish(topic_path, data=msg_bytes)
    log.info(f"Queued on pubsub for: {processor_event.instrument_name}")


def get_filtered_instruments(
    sftp: SFTP, case_mover: CaseMover
) -> Dict[str, Instrument]:
    instruments = sftp.get_instrument_folders()
    instruments = case_mover.filter_existing_instruments(instruments)
    instruments = sftp.get_instrument_files(instruments)
    instruments = sftp.filter_instrument_files(instruments)
    instruments = sftp.generate_bdbx_md5s(instruments)
    return instruments