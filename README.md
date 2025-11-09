# Blaise NISRA Case Mover

NISRA currently manages a Blaise web collection solution for us. Routinely, they upload the survey data to an SFTP server.

This service:
- Downloads data from the SFTP server
- Checks MD5 hashes of files to detect changes and avoid unnecessary processing
- Re-uploads new/modified files to a GCP storage bucket 
- Triggers asynchronous processing via Pub/Sub for changed files only
- Makes calls to our [REST API](https://github.com/ONSdigital/blaise-api-rest) for data processing

Additionally, it includes a cloud function that:
- Monitors if NISRA data has been properly processed
- Sends email alerts if updates haven't been received within expected timeframes
- Notifies relevant teams if questionnaires are missing from the bucket

## Local Development Setup

Install dependencies:

```
poetry install
```

Create an `.env` file in the root of the project with the required environment variables:

| Environment Variable | Description | Example |
| --- | --- |--- |
| SURVEY_SOURCE_PATH | Location on SFTP where survey data is held | `ONS/OPN/` |
| NISRA_BUCKET_NAME | Name of the bucket to upload survey data | `ons-blaise-v2-<env>-nisra` |
| SFTP_PORT | SFTP port | `22` |
| SFTP_HOST | SFTP hostname | `localhost` |
| SFTP_USERNAME | SFTP username | `sftp-test` |
| SFTP_PASSWORD | SFTP password | `<password>` |
| BLAISE_API_URL | URL for our REST API | `localhost:90` |
| SERVER_PARK | Name of the Blaise server park where questionnaires are installed | `gusty` |
| PROJECT_ID | The GCP project ID. | `ons-blaise-v2-env` |
| PROCESSOR_TOPIC_NAME | Pub/Sub topic to kick off processor | `ons-blaise-v2-<env>-nisra-process` |
| TEST_DATA_BUCKET | Name of the bucket used for test data during integration tests | `ons-blaise-v2-<env>-test-data` |

Example `.env` file:

```
SURVEY_SOURCE_PATH=./ONS/OPN/
NISRA_BUCKET_NAME='ons-blaise-v2-<env>-nisra
SFTP_PORT=22
SFTP_HOST=localhost
SFTP_USERNAME=sftp-test
SFTP_PASSWORD=<password>
BLAISE_API_URL=localhost:90
SERVER_PARK=gusty
PROJECT_ID=ons-blaise-v2-<env>
PROCESSOR_TOPIC_NAME=ons-blaise-v2-<env>-nisra-process
TEST_DATA_BUCKET='ons-blaise-v2-<env>-test-data
```

Our non-prod GCP environments have an SFTP for testing purposes. Run the following gcloud command to create a local tunnel
to the test server: 

```bash
gcloud compute start-iap-tunnel "sftp-test" "22" --zone "europe-west2-a" --project "ons-blaise-v2-<env>" --local-host-port=localhost:22
```

TODO: finish local dev setup instructions, tunnel to rest api, bucket access, etc...

## Tests

The following `make` commands are available for running tests:

Unit tests:

```bash
make test
```

Integration tests:

```bash
make integration-test
```

