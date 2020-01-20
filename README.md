# Blaise NISRA case mover (SFTP)
This app connects to the SFTP server where NISRA drops files and copies any changed ones to a bucket in GCP.

The .yaml.tpl specifies the variables for the SFTP connection (stored as secrets in GCP), as well as the following environment variables: 

              - name: SURVEY_DESTINATION_PATH
                value: 'OPN/opn1911a/'
              - name: SURVEY_SOURCE_PATH_PREFIX
                value: 'ONS/'
              - name: NISRA_BUCKET_NAME
                value: 'nisra-transfer'

A new .yaml.tpl file has to be created for different survey periods, adjusting the SURVEY_DESTINATION_PATH and container and cronjob name.

## Integration with GCP and Cloudbuild 
(Note GitOps integration currently only works with bncm-cronjob.yaml.tpl)

The repo now contains the following files to achieve CI\CD integration:

- known_hosts - this file is part of the repo and is used as part of the SSH process
- id_rsa.enc - this file contains a public key for the SSH process
- .tpl file - template yaml used to create the manifest
- cloudbuild.yaml - this contains the deployment scripts

When a pull request is created (on the dev branch of the corresponding repo - so blaise-nisra-case-mover-sftp) - this initiates the build via a GCP Trigger with a trigger type of 'Pull request' for the dev branch. 

The cloudbuild.yaml does the following:-

1. A docker image is built and pushed to the Google Container Registry, using SHORT_SHA as a tag. The SHORT_SHA (this is a unique identifier based on the git commit).

2. The service account connects to GitHub (using an SSH key decrypted by gcloud) in order to access the k8s repository, the SSH steps are as follows:-
Three SSH steps are carried out:

        * GCloud decrypts file containing the SSH key and stores it in a volume named ssh
        * Set up git with key and domain adding it to the known_hosts file
        * Connects to the k8s repository - using key in ssh volume
        
3. Clones the k8s repository candidate branch.

4. Generates the new manifest - so this uses the bcv.yaml.tpl for the 'Deployment' (template file), creates and updates bcv.yaml file on the candidate branch. ( A GCP Trigger on the candidate branch initiates a build based on the cloudbuild-delivery.yaml ).  This version of the bsm.yaml contains the SHORT_SHA from step 1.

5. The k8s repository carries out the deployment. If successful it copies the new bsm.yaml to the dev branch in the k8s repo.

6. Upon successful build of step 4 and 5 - it copies and does a commit (push) of the manifest (containing the bcv.yaml file) to the dev branch of the k8s repo ( A GCP Trigger on the dev branch initiates a build based on the cloudbuild-delivery.yaml ).

