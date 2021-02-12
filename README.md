# Blaise Nisra Case Mover

[![codecov](https://codecov.io/gh/ONSdigital/blaise-nisra-case-mover/branch/main/graph/badge.svg)](https://codecov.io/gh/ONSdigital/blaise-nisra-case-mover)

NISRA host an online Blaise web collection solution on our behalf. They periodically upload the results to an SFTP server.

This service downloads the data from the SFTP and re-uploads it to a GCP storage bucket, then calls the 
[Blaise Rest API](https://github.com/ONSdigital/blaise-api-rest) which will then pickup this data for further processing.


### Setup for Local development


| Environment Variable | Description                                                                                                                                                                                                                                    | Example                            |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| SURVEY_SOURCE_PATH   | Where on the sftp sever should the system look for the intstruments.                                                                                                                                                                           | ONS/OPN/                           |
| NISRA_BUCKET_NAME    | Name of the bucket to upload the downloaded SFTP files too.                                                                                                                                                                                    | ons-blaise-<env>-nisra             |
| TEST_DATA_BUCKET     | Not needed for running Case Mover, but used for behave intergration tests, this is where the Test data is pulled from.                                                                                                                         | ons-blaise-<br><env><br>-test-data |
| SFTP_PORT            | Connection information to SFTP server.                                                                                                                                                                                                         | 22                                 |
| SFTP_HOST            | Connection information to SFTP server.                                                                                                                                                                                                         | localhost:22                       |
| SFTP_USERNAME        | Connection information to SFTP server.                                                                                                                                                                                                         | sftp-test                          |
| SFTP_PASSWORD        | Connection information to SFTP server.                                                                                                                                                                                                         | t4734rfsdfyds7                     |
| BLAISE_API_URL       | Url the [Blaise Rest API](https://github.com/ONSdigital/blaise-api-rest) is running on, this is called once new data is uploaded to the Bucket.<br>For local development, you can port forward to the restapi VM simualrly to the SFTP server. | localhost:90                       |
| SERVER_PARK          | Main server park for Blaise, this is passed to the call to the Blaise Rest API.                                                                                                                                                                | gusty                              |
| FLASK_ENV            | For local development set this to `development` so that the system will use your local key.json for authenication with GCP Buckets.                                                                                                            | development                        |

Create a .env file with the following environment variables:

```
SURVEY_SOURCE_PATH = 'ONS/OPN/'
NISRA_BUCKET_NAME = 'ons-blaise-<env>-nisra'
TEST_DATA_BUCKET = 'ons-blaise-<env>-test-data'
SFTP_PORT = '2222'
SFTP_HOST = 'localhost'
SFTP_USERNAME = 'sftp-test'
SFTP_PASSWORD = '<password>'
BLAISE_API_URL='localhost:90'
SERVER_PARK='gusty'
FLASK_ENV=development
```

This configuration will attempt to process all OPN instruments found on a local SFTP server.

##### Connect to GCP Environment for Bucket and sftp server access:

The GCP environments have an SFTP server for testing purposes. Run the following gcloud command to create a local tunnel to the test server:

```bash
gcloud compute start-iap-tunnel "sftp-test" "22" --zone "europe-west2-b" --project "ons-blaise-<env>" --local-host-port=localhost:2222
```

Refer to the .tfstate file for the environment to locate the password, you can find this with the name `sftp_password`.

To access the GCP buckets remotely, [obtain a JSON service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) for the Default App Engine Service account which has access to the Nisra and test data bucket, place this in a key.json file at the root of
the project.

##### Create a virtual environment:

On MacOS
```
python3 -m venv venv  
source venv/bin/activate
```
On Windows
```
python -m venv venv  
venv\Scripts\activate
```

##### Run the flask server:
Start the Flask sever:
```bash
python main.py
```

By default, this will start the server on port 5000, open a browser and navigate to http://localhost:5000, to start the main process. 


### Testing

#### Unit tests

To run the unit test for the project, from the root of the project, run: 
```bash
pytest --cov=./ tests/*
```

#### Behave tests locally

To run the behaviour tests locally you will need to set up your environment for local development as explained in the section above.

Then from your virtual environment, run:
```bash
behave
```

You will see the logs outputted from Nisra Case Mover as it runs. With a summary outputed at the end.
```bash 
1 feature passed, 0 failed, 0 skipped
2 scenarios passed, 0 failed, 0 skipped
8 steps passed, 0 failed, 0 skipped, 0 undefined
```

#### Behave tests in a GCP environment

To run the Behave tests in a GCP environment and deploy a test version to app engine, run the following command, changing the substitutions variables. **NOTE:** The _PR_NUMBER env variable is required but does not affect the tests.
```bash
gcloud builds submit --config cloudbuild_test.yaml --substitutions=_PROJECT_ID=ons-blaise-v2-dev-test,\
_SFTP_HOST='10.6.0.2',_SFTP_USERNAME='sftp-test',_SFTP_PASSWORD='unique_password',_SFTP_PORT=22,\
_SURVEY_SOURCE_PATH=ONS/OPN/,_NISRA_BUCKET_NAME=ons-blaise-v2-dev-test-nisra,_TEST_DATA_BUCKET=ons-blaise-v2-dev-test-test-data,\
_BLAISE_API_URL='url',_SERVER_PARK='park',_PR_NUMBER=50
```

### Manually deploying to environment

To deploy to App Engine in an environment, from the root of the project run the following command, changing the substitutions variables. **Note:** The Slack variables are not required for non-formal environments.
```bash
gcloud builds submit --config cloudbuild.yaml --substitutions=_PROJECT_ID=ons-blaise-v2-dev-test,\
_SFTP_HOST='10.6.0.2',_SFTP_USERNAME='sftp-test',_SFTP_PASSWORD='unique_password',_SFTP_PORT=22,\
_SURVEY_SOURCE_PATH=ONS/OPN/,_NISRA_BUCKET_NAME=ons-blaise-v2-dev-test-nisra,\
_BLAISE_API_URL='restapi.europe-west2-a.c.ons-blaise-v2-dev-test.internal:90',_SERVER_PARK='gusty',\
_SLACK_CHANNEL=test,_SLACK_WEBHOOK=test
```


Copyright (c) 2021 Crown Copyright (Government Digital Service)
