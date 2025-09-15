import base64
import logging
import time

import pysftp
import requests
from google.cloud import pubsub_v1
from paramiko.ssh_exception import SSHException
from redo import retry

import cloud_functions.nisra_changes_checker
from models.configuration.blaise_config_model import BlaiseConfig
from models.configuration.bucket_config_model import BucketConfig
from models.configuration.notification_config_model import NotificationConfig
from models.processor_event import ProcessorEvent
from pkg.case_mover import CaseMover
from pkg.config import Config
from pkg.google_storage import init_google_storage
from pkg.sftp import SFTP, SFTPConfig
from pkg.trigger import get_filtered_instruments, trigger_processor
from processor import process_instrument
from services.blaise_service import BlaiseService
from services.google_bucket_service import GoogleBucketService
from services.nisra_update_check_service import NisraUpdateCheckService
from services.notification_service import NotificationService
from util.service_logging import setupLogging


def public_ip_logger():
    try:
        public_ip = requests.get("https://checkip.amazonaws.com").text.strip()
        logging.info("Public IP address - " + public_ip)
    except:
        logging.warning("Unable to lookup public IP address")


def ssh_retry_logger():
    logging.info("Retrying for SSH Exception")


def trigger(request):
    setupLogging()

    return retry(
        do_trigger,
        attempts=3,
        sleeptime=15,
        retry_exceptions=(SSHException),
        cleanup=ssh_retry_logger,
        args=(request,),
        kwargs={},
    )


def do_trigger(request, _content=None):
    try:
        survey = request.get_json()["survey"]
        config = Config.from_env()
        sftp_config = SFTPConfig.from_env()
        config.log()
        survey_source_path = survey
        sftp_config.log()
        publisher_client = pubsub_v1.PublisherClient()

        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        cnopts.compression = True

        google_storage = init_google_storage(config)
        if google_storage.bucket is None:
            return "Connection to bucket failed", 500

        public_ip_logger()
        logging.info("Connecting to SFTP server")
        with pysftp.Connection(
            host=sftp_config.host,
            username=sftp_config.username,
            password=sftp_config.password,
            port=int(sftp_config.port),
            cnopts=cnopts,
        ) as sftp_connection:
            logging.info("Connected to SFTP server")

            sftp = SFTP(sftp_connection, sftp_config, config)
            case_mover = CaseMover(google_storage, config, sftp)
            instruments = get_filtered_instruments(sftp, case_mover, survey_source_path)
            logging.info(f"Processing survey - {survey_source_path}")

            if len(instruments) == 0:
                logging.info("No instrument folders found after filtering")
                return "No instrument folders found, exiting", 200

            for instrument_name, instrument in instruments.items():
                trigger_processor(
                    publisher_client,
                    config,
                    ProcessorEvent(
                        instrument_name=instrument_name, instrument=instrument
                    ),
                )
    except Exception as error:
        logging.error(f"{error.__class__.__name__}: {error}", exc_info=True)


def processor(*args, **kwargs):
    setupLogging()
    retry(
        do_processor,
        attempts=3,
        sleeptime=15,
        retry_exceptions=(SSHException),
        cleanup=ssh_retry_logger,
        args=args,
        kwargs=kwargs,
    )


def do_processor(event, _context):
    try:
        logging.info("Pausing for 15 seconds")
        time.sleep(15)
        logging.info("Unpaused")
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

        public_ip_logger()
        logging.info("Connecting to SFTP server")
        with pysftp.Connection(
            host=sftp_config.host,
            username=sftp_config.username,
            password=sftp_config.password,
            port=int(sftp_config.port),
            cnopts=cnopts,
        ) as sftp_connection:
            logging.info("Connected to SFTP server")

            sftp = SFTP(sftp_connection, sftp_config, config)
            case_mover = CaseMover(google_storage, config, sftp)

            processor_event = ProcessorEvent.from_json(
                base64.b64decode(event["data"]).decode("utf-8")
            )

            logging.info(f"Processing instrument: {processor_event.instrument_name}")

            process_instrument(
                case_mover, processor_event.instrument_name, processor_event.instrument
            )
        logging.info("Closing SFTP connection")
    except Exception as error:
        logging.error(f"{error.__class__.__name__}: {error}", exc_info=True)


def nisra_changes_checker(_request):
    setupLogging()
    logging.info("Running Cloud Function - nisra_changes_checker")

    blaise_config = BlaiseConfig.from_env()
    blaise_service = BlaiseService(config=blaise_config)

    bucket_config = BucketConfig.from_env()
    bucket_service = GoogleBucketService(config=bucket_config)

    notification_config = NotificationConfig.from_env()
    notification_service = NotificationService(notification_config)

    nisra_update_check_service = NisraUpdateCheckService(
        blaise_service=blaise_service,
        bucket_service=bucket_service,
        notification_service=notification_service,
    )

    logging.info("Created nisra_update_check_service")

    return cloud_functions.nisra_changes_checker.nisra_changes_checker(
        nisra_update_check_service=nisra_update_check_service
    )
