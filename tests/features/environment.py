import base64
import logging
import os

import pysftp
from google.cloud.pubsub_v1 import PublisherClient

import main
from app.app import app, load_config
from pkg.google_storage import GoogleStorage


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


def before_feature(context, feature):
    app.testing = True
    load_config(app)
    context.app = app
    context.app.publisher_client = FakePublisherClient()
    context.client = app.test_client()


def after_scenario(context, scenario):
    print(f"Published messages: {context.app.publisher_client.published_messages}")
    context.app.publisher_client.published_messages = []
    google_storage = GoogleStorage(
        os.getenv("NISRA_BUCKET_NAME", "env_var_not_set"), logging
    )
    google_storage.initialise_bucket_connection()
    if google_storage.bucket is None:
        print("Failed")

    blobs = google_storage.list_blobs()

    google_storage.delete_blobs(blobs)

    sftp_host = os.getenv("SFTP_HOST", "env_var_not_set")
    sftp_username = os.getenv("SFTP_USERNAME", "env_var_not_set")
    sftp_password = os.getenv("SFTP_PASSWORD", "env_var_not_set")
    sftp_port = os.getenv("SFTP_PORT", "env_var_not_set")
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
        host=sftp_host,
        username=sftp_username,
        password=sftp_password,
        port=int(sftp_port),
        cnopts=cnopts,
    ) as sftp:
        sftp.execute("rm -rf ~/ONS/TEST/OPN2101A")
