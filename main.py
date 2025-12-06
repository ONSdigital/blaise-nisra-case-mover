import base64
import logging
import time
import os

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
from util.sftp_connection import sftp_connection

setupLogging()

publisher_client = pubsub_v1.PublisherClient()

def public_ip_logger():
    try:
        public_ip = requests.get("https://checkip.amazonaws.com", timeout=5).text.strip()
        logging.info(f"Public IP address - {public_ip}")
    except Exception:
        logging.warning("Unable to lookup public IP address")

def ssh_retry_logger():
    logging.info("Retrying for SSH Exception")

def trigger(request):
    def retry_and_return():
        retry(
            do_trigger,
            attempts=3,
            sleeptime=15,
            retry_exceptions=(SSHException),
            cleanup=ssh_retry_logger,
            args=(request,),
            kwargs={},
        )
        return "Done"

    return retry_and_return()

def do_trigger(request, _content=None):
    try:
        request_json = request.get_json()
        if not request_json or "survey" not in request_json:
            logging.error("Invalid request: 'survey' field missing.")
            return "Invalid Request", 400
            
        survey_source_path = request_json["survey"]
        
        config = Config.from_env()
        sftp_config = SFTPConfig.from_env()
        
        config.log()
        sftp_config.log()

        google_storage = init_google_storage(config)
        if google_storage.bucket is None:
            return "Connection to bucket failed", 500

        public_ip_logger()
        logging.info("Connecting to SFTP server")

        with sftp_connection(sftp_config) as sftp_conn:
            logging.info("Connected to SFTP server")

            sftp = SFTP(sftp_conn, sftp_config, config)
            case_mover = CaseMover(google_storage, config, sftp)

            instruments = get_filtered_instruments(sftp, case_mover, survey_source_path)
            logging.info(f"Processing survey - {survey_source_path}")

            if not instruments:
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

        logging.info("SFTP connection closed")

    except Exception as error:
        logging.error(f"{error.__class__.__name__}: {error}", exc_info=True)
        raise error

def processor(*args, **kwargs):
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
        config = Config.from_env()
        sftp_config = SFTPConfig.from_env()
        
        google_storage = init_google_storage(config)
        if google_storage.bucket is None:
            logging.error("Connection to bucket failed")
            raise Exception("Connection to bucket failed")

        public_ip_logger()

        processor_event = ProcessorEvent.from_json(
            base64.b64decode(event["data"]).decode("utf-8")
        )
        
        logging.info(f"Processing instrument: {processor_event.instrument_name}")
        logging.info("Connecting to SFTP server")
        
        with sftp_connection(sftp_config) as sftp_conn:
            logging.info("Connected to SFTP server")

            sftp = SFTP(sftp_conn, sftp_config, config)
            case_mover = CaseMover(google_storage, config, sftp)

            process_instrument(
                case_mover, processor_event.instrument_name, processor_event.instrument
            )
            
    except Exception as error:
        logging.error(f"{error.__class__.__name__}: {error}", exc_info=True)
        raise error

def nisra_changes_checker(_request):
    logging.info("Running Cloud Function - nisra_changes_checker")

    blaise_config = BlaiseConfig.from_env()
    bucket_config = BucketConfig.from_env()
    notification_config = NotificationConfig.from_env()

    nisra_update_check_service = NisraUpdateCheckService(
        blaise_service=BlaiseService(config=blaise_config),
        bucket_service=GoogleBucketService(config=bucket_config),
        notification_service=NotificationService(notification_config),
    )

    logging.info("Created nisra_update_check_service")

    return cloud_functions.nisra_changes_checker.nisra_changes_checker(
        nisra_update_check_service=nisra_update_check_service
    )