from behave import *


@given("there is new OPN NISRA data on the NISRA SFTP that hasn't previously been transferred")
def step_imp(context):
    pass


@given("there is no new OPN NISRA data on the NISRA SFTP")
def step_imp(context):
    pass


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
