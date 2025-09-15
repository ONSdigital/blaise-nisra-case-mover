import base64
import logging
import os
import sys

import pysftp
from google.cloud.pubsub_v1 import PublisherClient

import main
from pkg.config import Config
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTPConfig
from util.service_logging import setupLogging

class FakePublisherClient(PublisherClient):
    def __init__(self):
        self.published_messages = []

    def publish(self, topic_path, data):
        message = {"topic_path": topic_path, "data": data}
        self.published_messages.append(message)

    def run_all(self):
        for message in self.published_messages:
            event = {"data": base64.encodebytes(message["data"])}
            main.processor(event, {})
    
def before_all(context):
    context.config = Config.from_env()
    context.sftp_config = SFTPConfig.from_env()


def before_feature(context, feature):
    setupLogging()
    context.mock_requests_post = None
    context.publisher_client = FakePublisherClient()
    

def after_scenario(context, scenario):
    logging.info(f"After Scenario cleanup")
    print(f"Published messages: {context.publisher_client.published_messages}")
    context.publisher_client.published_messages = []  

    google_storage = GoogleStorage(os.getenv("NISRA_BUCKET_NAME", "env_var_not_set"))
    google_storage.initialise_bucket_connection()
    logging.info(f"After Scenario Bucket connection successful")
    if google_storage.bucket is None:
        logging.info(f"After Scenario Google storage issue")

    blobs = google_storage.list_blobs()
    logging.info(f"After Scenario list blobs successful")
    logging.info(google_storage.list_blobs())

    google_storage.delete_blobs(blobs)
    logging.info(f"After Scenario delete blobs successful")

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(
        host=context.sftp_config.host,
        username=context.sftp_config.username,
        password=context.sftp_config.password,
        port=int(context.sftp_config.port),
        cnopts=cnopts,
    ) as sftp:
        sftp.execute("rm -rf ~/ONS/TEST/OPN2101A")
    logging.info(f"After Scenario SFTP successful")

def after_feature(context, feature):
    context = None