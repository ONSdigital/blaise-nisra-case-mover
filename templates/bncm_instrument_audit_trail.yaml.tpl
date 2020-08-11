apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: bncm-opn2004a-audit-trail
spec:
  schedule: "10,40 * * * *"
  successfulJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: bncm-opn2004a-audit-trail
            image: "eu.gcr.io/ons-blaise-dev/blaise-nisra-case-mover:COMMIT_SHA"
            env:
              - name: AUDIT_TRAIL
                value: 'TRUE'
              - name: INSTRUMENT_SOURCE_PATH
                value: 'ONS/OPN/opn2004a/'
              - name: SURVEY_SOURCE_PATH
                value: ''
              - name: INSTRUMENT_DESTINATION_PATH
                value: 'ONS/'
              - name: NISRA_BUCKET_NAME
                value: 'ons-blaise-dev-nisra'
              - name: SFTP_HOST
                valueFrom:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_HOST
              - name: SFTP_USERNAME
                valueFrom:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_USERNAME
              - name: SFTP_PASSWORD
                valueFrom:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_PASSWORD
              - name: SFTP_PORT
                valueForm:
                  secretKeyRef:
                    name: nisra-sftp
                    key: SFTP_PORT
          restartPolicy: OnFailure