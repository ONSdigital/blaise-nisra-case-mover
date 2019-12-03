apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: nisra-mover-opn1911a-audit-trail
spec:
  schedule: "0 0 1 * *"
  successfulJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: nisra-mover-opn1911a-audit-trail-container
            image: "eu.gcr.io/blaisepoc/blaise-nisra-case-mover-sftp:COMMIT_SHA"
            env:
              - name: AUDIT_TRAIL
                value: 'TRUE'
              - name: SURVEY_DESTINATION_PATH
                value: 'OPN/opn1911a/'
              - name: SURVEY_SOURCE_PATH_PREFIX
                value: 'ONS/'
              - name: NISRA_BUCKET_NAME
                value: 'nisra-transfer'
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
                valueForm:
                  secretKeyRef:
                    name: nisrasftp
                    key: SFTP_PORT
          restartPolicy: OnFailure