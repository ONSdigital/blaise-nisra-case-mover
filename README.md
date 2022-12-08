# Blaise Nisra Case Mover

[![codecov](https://codecov.io/gh/ONSdigital/blaise-nisra-case-mover/branch/main/graph/badge.svg)](https://codecov.io/gh/ONSdigital/blaise-nisra-case-mover)
[![CI status](https://github.com/ONSdigital/blaise-nisra-case-mover/workflows/Test%20coverage%20report/badge.svg)](https://github.com/ONSdigital/blaise-nisra-case-mover/workflows/Test%20coverage%20report/badge.svg)
<img src="https://img.shields.io/github/release/ONSdigital/blaise-nisra-case-mover.svg?style=flat-square" alt="Nisra Case Mover release verison">

NISRA host an online Blaise web collection solution on our behalf. They periodically upload the results to an SFTP server.

This service downloads the data from the SFTP and re-uploads it to a GCP storage bucket, then calls the
[Blaise Rest API](https://github.com/ONSdigital/blaise-api-rest) which will then pick up this data for further processing.


### Setup for Local development

| Environment Variable | Description                                                                                                                                                                                                                                    | Example                            |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| SURVEY_SOURCE_PATH   | Where on the sftp sever should the system look for the instruments.                                                                                                                                                                            | `ONS/OPN/`                         |
| NISRA_BUCKET_NAME    | Name of the bucket to upload the downloaded SFTP files too.                                                                                                                                                                                    | `ons-blaise-env-nisra`             |
| TEST_DATA_BUCKET     | Not needed for running Case Mover, but used for behave integration tests, this is where the Test data is pulled from.                                                                                                                          | `ons-blaise-env-test-data`         |
| SFTP_PORT            | Connection information to SFTP server.                                                                                                                                                                                                         | `22`                               |
| SFTP_HOST            | Connection information to SFTP server.                                                                                                                                                                                                         | `localhost`                        |
| SFTP_USERNAME        | Connection information to SFTP server.                                                                                                                                                                                                         | `sftp-test`                        |
| SFTP_PASSWORD        | Connection information to SFTP server.                                                                                                                                                                                                         | `t4734rfsdfyds7`                   |
| BLAISE_API_URL       | Url the [Blaise Rest API](https://github.com/ONSdigital/blaise-api-rest) is running on, this is called once new data is uploaded to the Bucket.<br>For local development, you can port forward to the restapi VM similarly to the SFTP server. | `localhost:90`                     |
| SERVER_PARK          | Main server park for Blaise, this is passed to the call to the Blaise Rest API.                                                                                                                                                                | `gusty`                            |
| PROJECT_ID           | The Google Cloud project ID for the environment the app is running against.                                                                                                                                                                    | `ons-blaise-v2-env`                |
| PROCESSOR_TOPIC_NAME | The topic name where                                                                                                                                                                                                                           | `ons-blaise-v2-env-nisra-process`  |
| TEST_DATA_BUCKET     | The bucket where the test data files exist for the integration tests (this is not needed for running the application, only testing).                                                                                                           | `ons-blaise-v2-dev-test-test-data` |

Create a .env file with the following environment variables:

```
export SURVEY_SOURCE_PATH='./ONS/OPN/'
export NISRA_BUCKET_NAME='ons-blaise-v2-<env>-nisra'
export TEST_DATA_BUCKET='ons-blaise-v2-<env>-test-data'
export SFTP_PORT='2222'
export SFTP_HOST='localhost'
export SFTP_USERNAME='sftp-test'
export SFTP_PASSWORD='<password>'
export BLAISE_API_URL='localhost:90'
export SERVER_PARK='gusty'
export PROJECT_ID=ons-blaise-v2-<env>
export PROCESSOR_TOPIC_NAME=ons-blaise-v2-<env>-nisra-process
export TEST_DATA_BUCKET=ons-blaise-v2-<test-env>-test-data
```

This configuration will attempt to process all OPN instruments found on a local SFTP server.

##### Connect to GCP Environment for Bucket and sftp server access:

The GCP environments have an SFTP server for testing purposes. Run the following gcloud command to create a local tunnel
to the test server:

```bash
gcloud compute start-iap-tunnel "sftp-test" "22" --zone "europe-west2-b" --project "ons-blaise-v2-<env>" --local-host-port=localhost:2222
```

Refer to the `.tfstate` file for the environment to locate the password, you can find this with the name `sftp_password`.

To access the GCP buckets remotely,
[obtain a JSON service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) for the
Default App Engine Service account which has access to the Nisra and test data bucket, save this as `key.json` and place
at the root of the project.

##### Install dependencies:

```
poetry install
```

### Testing

#### Unit tests

To run the unit test for the project, from the root of the project, run:

```bash
make test
```

#### Behave tests locally

To run the behaviour tests locally you will need to set up your environment for local development as explained in the
section above.

Then run:

```bash
make integration-test
```

You will see the logs outputted from Nisra Case Mover as it runs. With a summary outputted at the end.
```bash
1 feature passed, 0 failed, 0 skipped
2 scenarios passed, 0 failed, 0 skipped
8 steps passed, 0 failed, 0 skipped, 0 undefined
```

Copyright (c) 2021 Crown Copyright (Government Digital Service)
