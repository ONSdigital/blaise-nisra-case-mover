import base64
import os

from google.cloud.pubsub_v1 import PublisherClient

import main
from pkg.config import Config
from pkg.google_storage import GoogleStorage
from pkg.sftp import SFTPConfig
from util.service_logging import setupLogging
from util.sftp_connection import sftp_connection


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
    context.publisher_client = FakePublisherClient()


def after_scenario(context, scenario):
    print(f"Published messages: {context.publisher_client.published_messages}")
    context.publisher_client.published_messages = []
    google_storage = GoogleStorage(os.getenv("NISRA_BUCKET_NAME", "env_var_not_set"))
    google_storage.initialise_bucket_connection()
    if google_storage.bucket is None:
        print("Failed")

    blobs = google_storage.list_blobs()

    google_storage.delete_blobs(blobs)

    with sftp_connection(context.sftp_config, allow_unknown_hosts=True) as sftp_conn:
        ssh_client = sftp_conn.get_channel().get_transport().open_session()
        try:
            print(f"Starting remote cleanup")
            ssh_client.exec_command("rm -rf ~/ONS/TEST/OPN2101A")
        except Exception as ssh_error:
            print(f"Failed to execute remote cleanup: {ssh_error}", exc_info=True)
