# blaise-nisra-case-mover

NISRA host an online Blaise web collection solution on our behalf. They periodically upload the results to an SFTP server.

This service downloads the data from the SFTP and re-uploads it to a GCP storage bucket, other services will then pickup this data for further processing. 

The service can be configured to process data at instrument level or survey level (will process all survey instruments found) via the yaml file. The example yamls in the templates folder are of kind cron so the service can be configured to run on a cron schedule.

### Run Locally

Change the following line in the blaise_nisra_case_mover.py file.
From:
```python
from config import *
```
To:
```python
from config_local import *
```
**Make sure not to commit this change**


Create a .env file with the following environment variables:

```
INSTRUMENT_SOURCE_PATH = ''
SURVEY_SOURCE_PATH = 'ONS/OPN/'
INSTRUMENT_DESTINATION_PATH = 'OPN/'
NISRA_BUCKET_NAME = 'ons-blaise-<env>-nisra'
SFTP_PORT = '2222'
SFTP_HOST = 'localhost'
SFTP_USERNAME = 'sftp-test'
SFTP_PASSWORD = '<password>'
```

This configuration will attempt to process all OPN instruments found on a local SFTP server.

The GCP environments have an SFTP server for testing purposes. Run the following gcloud command to create a local tunnel to the test server:

```bash
gcloud compute start-iap-tunnel "sftp-test" "22" --zone "europe-west2-b" --project "ons-blaise-<env>" --local-host-port=localhost:2222
```

Refer to the .tfstate file for the environment to locate the password.

Create a service account that has permission to the bucket and generate a JSON key, place this in a key.json file within the project.
