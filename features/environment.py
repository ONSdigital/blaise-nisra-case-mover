import logging

import pysftp

from blaise_nisra_case_mover import app
from google_storage import GoogleStorage


def before_feature(context, feature):
    app.testing = True
    context.client = app.test_client()

def after_scenario(context, scenario):
    googleStorage = GoogleStorage('ons-blaise-v2-dev-rich-01-nisra', logging)
    googleStorage.initialise_bucket_connection()
    if googleStorage.bucket is None:
        print("Failed")

    blobs = googleStorage.list_blobs()

    googleStorage.delete_blobs(blobs)

    sftp_host = 'localhost'
    sftp_username = 'sftp-test'
    sftp_password = 'DUMMY_PASSWORD'
    sftp_port = '2222'

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    with pysftp.Connection(
            host=sftp_host,
            username=sftp_username,
            password=sftp_password,
            port=int(sftp_port),
            cnopts=cnopts,
    ) as sftp:
        sftp.execute("rm -rf ~/ONS/OPN/OPN2101A")
