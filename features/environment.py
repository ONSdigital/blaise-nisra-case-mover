import logging
import os

import pysftp
from blaise_nisra_case_mover import app
from google_storage import GoogleStorage


def before_feature(context, feature):
    app.testing = True
    context.client = app.test_client()


def after_scenario(context, scenario):
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

    with pysftp.Connection(
        host=sftp_host,
        username=sftp_username,
        password=sftp_password,
        port=int(sftp_port),
    ) as sftp:
        sftp.execute("rm -rf ~/ONS/TEST/OPN2101A")
