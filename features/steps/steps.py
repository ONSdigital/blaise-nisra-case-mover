from behave import *


@given("there is new OPN NISRA data on the NISRA SFTP that hasn't previously been transferred")
def step_imp(context):
    pass

    # for file in file_list:
    #     blob = googleStorage.get_blob(f"opn2101a-nisra/{file}")
    #     blob.download_to_filename(blob.name)

    sftp_host = 'localhost'
    sftp_username = 'sftp-test'
    sftp_password = 'DUMMY_PASSWORD'
    sftp_port = '2222'

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None

    # with pysftp.Connection(
    #         host=sftp_host,
    #         username=sftp_username,
    #         password=sftp_password,
    #         port=int(sftp_port),
    #         cnopts=cnopts,
    # ) as sftp:
    #     sftp.mkdir("ONS/OPN/OPN2101A/")
    #
    #     for file in file_list:
    #         sftp.put(f"opn2101a-nisra/{file}", f"ONS/OPN/OPN2101A/{file}")


@when("the nisra-mover service is run with an OPN configuration")
def step_imp(context):
    pass


@then("the new data is copied to the GCP storage bucket including all necessary support files")
def step_imp(context):
    pass


@then("no data is copied to the GCP storage bucket")
def step_imp(context):
    pass


@then("a call is made to the RESTful API to process the new data")
def step_imp(context):
    pass


@then("a call is not made to the RESTful API to process the new data")
def step_imp(context):
    pass
