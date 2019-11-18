apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: nisra-mover
spec:
  schedule: "*/30 * * * *"
  successfulJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          volumes:
            - name: nisra-mover-pv-storage
              persistentVolumeClaim:
                claimName: nisra-mover-pv-claim
          containers:
          - name: nisra-mover-container
            image: "eu.gcr.io/blaisepoc/blaise-nisra-case-mover-sftp:COMMIT_SHA"
            volumeMounts:
              - mountPath: "/mnt/data"
                name: nisra-mover-pv-storage
            env:
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
                valueFrom:
                  secretKeyRef:
                    name: nisrasftp
                    key: SFTP_PORT
          restartPolicy: OnFailure