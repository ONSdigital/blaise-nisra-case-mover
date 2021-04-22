import logging
import os

import pysftp

from app.app import app, load_config
from pkg.google_storage import GoogleStorage


def before_feature(context, feature):
    app.testing = True
    load_config(app)
    context.app = app
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
