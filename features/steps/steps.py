import logging
import os
from pathlib import Path
from unittest import mock

import pysftp
from behave import *

from google_storage import GoogleStorage


@given("there is no new OPN NISRA data on the NISRA SFTP")
def step_there_is_no_new_OPN_NISRA_data_on_the_NISRA_SFTP(context):
    pass


@given("there is new OPN NISRA data on the NISRA SFTP that hasn't previously been transferred")
def step_there_is_new_OPN_NISRA_data_on_the_NISRA_SFTP_that_hasnt_previously_been_transferred(context):
    os.environ["google_application_credentials"] = "key.json"
    googleStorage = GoogleStorage('ons-blaise-v2-dev-rich-01-test-data', logging)
    googleStorage.initialise_bucket_connection()
    if googleStorage.bucket is None:
        print("Failed")

    file_list = [
        "FrameEthnicity.blix",
        "FrameSOC2010.blix",
        "FrameSOC2K.blix",
        "OPN2101A.bdbx",
        "OPN2101A.bmix",
        "OPN2101A.bdix"
    ]

    if not Path("opn2101a-nisra").exists:
        os.mkdir("opn2101a-nisra")

    for file in file_list:
        blob = googleStorage.get_blob(f"opn2101a-nisra/{file}")
        blob.download_to_filename(blob.name)

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

        try:
            sftp.execute("rm -rf ~/ONS/OPN/OPN2101A")
        finally:
            sftp.mkdir("ONS/OPN/OPN2101A/")

        for file in file_list:
            sftp.put(f"opn2101a-nisra-test/{file}", f"ONS/OPN/OPN2101A/{file}")


@when("the nisra-mover service is run with an OPN configuration")
def step_the_nisra_mover_service_is_run_with_an_OPN_configuration(context):
    with mock.patch("requests.post") as mock_requests_post:
        mock_requests_post.return_value.status_code = 200
        context.page = context.client.get('/')
        context.mock_requests_post = mock_requests_post


@then("the new data is copied to the GCP storage bucket including all necessary support files")
def step_the_new_data_is_copied_to_the_GCP_storage_bucket_including_all_necessary_support_files(context):
    googleStorage = GoogleStorage('ons-blaise-v2-dev-rich-01-nisra', logging)
    googleStorage.initialise_bucket_connection()
    if googleStorage.bucket is None:
        print("Failed")

    file_list = [
        "OPN2101A/FrameEthnicity.blix",
        "OPN2101A/FrameSOC2010.blix",
        "OPN2101A/FrameSOC2K.blix",
        "OPN2101A/OPN2101A.bdbx",
        "OPN2101A/OPN2101A.bmix",
        "OPN2101A/OPN2101A.bdix"
    ]

    bucket_items = []

    for blob in googleStorage.list_blobs():
        bucket_items.append(blob.name)

    file_list.sort()
    bucket_items.sort()

    assert bucket_items == file_list


@then("no data is copied to the GCP storage bucket")
def step_no_data_is_copied_to_the_GCP_storage_bucket(context):
    pass


@then("a call is made to the RESTful API to process the new data")
def step_a_call_is_made_to_the_RESTful_API_to_process_the_new_data(context):
    context.mock_requests_post.assert_called_once_with(
        "http://env_var_not_set/api/vi/serverpark/env_var_not_set/instruments/OPN2101A/data",
        data='{"InstrumentDataPath": "OPN2101A"}',
        headers={"content-type": "application/json"}
    )


@then("a call is not made to the RESTful API to process the new data")
def step_a_call_is_not_made_to_the_RESTful_API_to_process_the_new_data(context):
    pass
