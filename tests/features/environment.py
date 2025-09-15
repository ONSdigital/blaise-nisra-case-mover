import logging
import os

import pysftp

from pkg.config import Config
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTPConfig
from tests.features.fake_publisher_client import FakePublisherClient
from util.service_logging import setupLogging


def before_all(context):
    context.config = Config.from_env()
    context.sftp_config = SFTPConfig.from_env()


def before_scenario(context, scenario):
    setupLogging()
    context.mock_requests_post = None
    context.publisher_client = FakePublisherClient()


def after_scenario(context, scenario):
    logging.info("After Scenario cleanup")
    print(f"Published messages: {context.publisher_client.published_messages}")
    context.publisher_client.published_messages = []

    google_storage = GoogleStorage(os.getenv("NISRA_BUCKET_NAME", "env_var_not_set"))
    google_storage.initialise_bucket_connection()
    logging.info("After Scenario Bucket connection successful")
    if google_storage.bucket is None:
        logging.info("After Scenario Google storage issue")

    blobs = google_storage.list_blobs()
    if not (blobs is None or blobs == []):
        google_storage.delete_blobs(blobs)
        logging.info("After Scenario delete blobs successful")

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(
        host=context.sftp_config.host,
        username=context.sftp_config.username,
        password=context.sftp_config.password,
        port=int(context.sftp_config.port),
        cnopts=cnopts,
    ) as sftp:
        try:
            sftp.execute("rm -rf ~/ONS/TEST/OPN2101A")
        except Exception:
            logging.error("error in sftp")
