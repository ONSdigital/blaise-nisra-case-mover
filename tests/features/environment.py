import base64
import os

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

    # cnopts = pysftp.CnOpts()
    # cnopts.hostkeys = None

    hostkeys = None
    if cnopts.hostkeys.lookup(host) is None:
        print("New host - will accept any host key")
        # Backup loaded .ssh/known_hosts file
        hostkeys = cnopts.hostkeys

        # And do not verify host key of the new host
        cnopts.hostkeys = None

    with pysftp.Connection(
        host=context.sftp_config.host,
        username=context.sftp_config.username,
        password=context.sftp_config.password,
        port=int(context.sftp_config.port),
        cnopts=cnopts,
    ) as sftp:
        if hostkeys is not None:
            print("Connected to new host, caching its hostkey")
            hostkeys.add(host, sftp.remote_server_key.get_name(), sftp.remote_server_key)
            hostkeys.save(pysftp.helpers.known_hosts())

        sftp.execute("rm -rf ~/ONS/TEST/OPN2101A")
