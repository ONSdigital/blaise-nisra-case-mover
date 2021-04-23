import logging
import os
from unittest import mock

import pysftp
from behave import given, then, when

from pkg.google_storage import GoogleStorage

file_list = [
    "FrameEthnicity.blix",
    "FrameSOC2010.blix",
    "FrameSOC2K.blix",
    "OPN2101A.bdbx",
    "OPN2101A.bmix",
    "OPN2101A.bdix",
]


@given("there is no new OPN NISRA data on the NISRA SFTP")
def step_there_is_no_new_opn_nisra_data_on_the_nisra_sftp(context):
    copy_opn2101a_files_to_sftp()
    nisra_google_storage = GoogleStorage(
        os.getenv("NISRA_BUCKET_NAME", "env_var_not_set"), logging
    )
    nisra_google_storage.initialise_bucket_connection()

    if nisra_google_storage.bucket is None:
        print("Failed")

    for file in file_list:
        nisra_google_storage.upload_file(file, f"opn2101a/{file}".lower())

    file_generation_list = []

    for blob in nisra_google_storage.list_blobs():
        file_generation_list.append(blob.generation)

    context.file_generation_list = file_generation_list.sort()


@given(
    "there is new OPN NISRA data on the NISRA SFTP that hasn't previously been transferred"  # noqa: E501
)
def step_there_is_new_opn_nisra_data_on_the_nisra_sftp_that_hasnt_previously_been_transferred(  # noqa: E501
    context,
):
    copy_opn2101a_files_to_sftp()


@when("the nisra-mover service is run with an OPN configuration")
def step_the_nisra_mover_service_is_run_with_an_opn_configuration(context):
    context.app.sftp_config.survey_source_path = "./ONS/TEST"
    with mock.patch("requests.post") as mock_requests_post:
        mock_requests_post.return_value.status_code = 200
        context.page = context.client.get("/")
        context.mock_requests_post = mock_requests_post


@when(
    "the nisra-mover service is run with the survey_source_path of {survey_source_path}"
)
def step_the_nisra_mover_service_is_run_with_survey_source_path(
    context, survey_source_path
):
    with mock.patch("requests.post") as mock_requests_post:
        mock_requests_post.return_value.status_code = 200
        context.page = context.client.get(f"/?survey_source_path={survey_source_path}")
        context.mock_requests_post = mock_requests_post


@then(
    "the new data is copied to the GCP storage bucket including all necessary support files"  # noqa: E501
)
def step_the_new_data_is_copied_to_the_gcp_storage_bucket_including_all_necessary_support_files(  # noqa: E501
    context,
):
    google_storage = GoogleStorage(
        os.getenv("NISRA_BUCKET_NAME", "env_var_not_set"), logging
    )
    google_storage.initialise_bucket_connection()

    if google_storage.bucket is None:
        print("Failed")

    bucket_file_list = [
        "opn2101a/frameethnicity.blix",
        "opn2101a/framesoc2010.blix",
        "opn2101a/framesoc2k.blix",
        "opn2101a/opn2101a.bdbx",
        "opn2101a/opn2101a.bmix",
        "opn2101a/opn2101a.bdix",
    ]

    bucket_items = []

    for blob in google_storage.list_blobs():
        bucket_items.append(blob.name)

    bucket_file_list.sort()
    bucket_items.sort()

    check = all(item in bucket_items for item in bucket_file_list)

    assert (
        check is True
    ), f"Bucket items {bucket_items}, did not match expected: {bucket_file_list}"


@then("no data is copied to the GCP storage bucket")
def step_no_data_is_copied_to_the_gcp_storage_bucket(context):
    google_storage = GoogleStorage(
        os.getenv("NISRA_BUCKET_NAME", "env_var_not_set"), logging
    )
    google_storage.initialise_bucket_connection()

    if google_storage.bucket is None:
        print("Failed")

    bucket_items = []

    for blob in google_storage.list_blobs():
        bucket_items.append(blob.generation)

    assert context.file_generation_list == bucket_items.sort()


@then("a call is made to the RESTful API to process the new data")
def step_a_call_is_made_to_the_restful_api_to_process_the_new_data(context):
    server_park = os.getenv("SERVER_PARK", "env_var_not_set")
    blaise_api_url = os.getenv("BLAISE_API_URL", "env_var_not_set")
    context.mock_requests_post.assert_called_once_with(
        (
            f"http://{blaise_api_url}/api/v1/serverparks/"
            f"{server_park}/instruments/opn2101a/data"
        ),
        json={"instrumentDataPath": "opn2101a"},
        headers={"content-type": "application/json"},
        timeout=10,
    )


@then("a call is not made to the RESTful API")
def step_a_call_is_not_made_to_the_restful_api(context):
    context.mock_requests_post.assert_not_called()


def copy_opn2101a_files_to_sftp():
    os.environ[
        "google_application_credentials"
    ] = "S:\\work\\code\\blaise-nisra-case-mover\\key.json"
    google_storage = GoogleStorage(
        os.getenv("TEST_DATA_BUCKET", "env_var_not_set"), logging
    )
    google_storage.initialise_bucket_connection()

    if google_storage.bucket is None:
        print("Failed")

    for file in file_list:
        blob = google_storage.get_blob(f"opn2101a-nisra/{file}")
        blob.download_to_filename(file)

    sftp_host = os.getenv("SFTP_HOST", "env_var_not_set")
    sftp_username = os.getenv("SFTP_USERNAME", "env_var_not_set")
    sftp_password = os.getenv("SFTP_PASSWORD", "env_var_not_set")
    sftp_port = os.getenv("SFTP_PORT", "env_var_not_set")

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    cnopts.compression = True

    with pysftp.Connection(
        host=sftp_host,
        username=sftp_username,
        password=sftp_password,
        port=int(sftp_port),
        cnopts=cnopts,
    ) as sftp:

        try:
            sftp.execute("rm -rf ~/ONS/TEST/OPN2101A")
        finally:
            sftp.mkdir("ONS/TEST/OPN2101A/")

        for file in file_list:
            sftp.put(f"{file}", f"ONS/TEST/OPN2101A/{file}")
