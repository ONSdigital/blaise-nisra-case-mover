apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: nisra-mover-opn2001a
spec:
  schedule: "*/60 * * * *"
  successfulJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: nisra-mover-opn2001a-container
            image: "eu.gcr.io/GOOGLE_CLOUD_PROJECT/blaise-nisra-case-mover-sftp:COMMIT_SHA"
            env:
              - name: SURVEY_DESTINATION_PATH
                value: 'opn/opn2001a/'
              - name: SURVEY_SOURCE_PATH_PREFIX
                value: 'ONS/'
              - name: NISRA_BUCKET_NAME
                valueFrom:
                  configMapKeyRef:
                    name: blaise-buckets
                    key: bucket-name-nisra
              - name: SFTP_HOST
                valueFrom:
                  secretKeyRef:
                    name: nisrasftp
                    key: SFTP_HOST
              - name: SFTP_USERNAME
                valueFrom:
                  secretKeyRef:
                    name: nisrasftp
                    key: SFTP_USERNAME
              - name: SFTP_PASSWORD
                valueFrom:
                  secretKeyRef:
                    name: nisrasftp
                    key: SFTP_PASSWORD
              - name: SFTP_PORT
                valueFrom:
                  secretKeyRef:
                    name: nisrasftp
                    key: SFTP_PORT
          restartPolicy: OnFailure
