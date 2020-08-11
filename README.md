# blaise-nisra-case-mover

NISRA host an online Blaise web collection solution on our behalf. They periodically upload the results to an SFTP server.

This service downloads the data from the SFTP and re-uploads it to a GCP storage bucket, other services will then pickup this data for further processing. 

The service can be configured to process data at instrument level or survey level (will process all survey instruments found) via the yaml file. The example yamls are of kind cron so the service can be configured to run on a cron schedule.