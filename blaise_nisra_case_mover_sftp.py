import os
import pysftp
import pybase64
import hashlib
from google.cloud import storage


def main():
    # Config details
    survey_destination_path = 'OPN/opn1911a/'
    survey_source_path = 'ONS/' + survey_destination_path
    bucket_name = 'nisra-transfer'
    file_list = ['opn1911a.manifest']

    try:
        print('Attempting sftp connection...')
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection(os.getenv('SFTP_HOST'),
                               username=os.getenv('SFTP_USERNAME'),
                               password=os.getenv('SFTP_PASSWORD'),
                               port=int(os.getenv('SFTP_PORT')),
                               cnopts=cnopts) as sftp:
            print('Connection established.')

            for file in file_list:
                print('Copying {} from SFTP server to container storage.'.format(file))
                sftp.get(survey_source_path + file, file)

                with open(file) as file_to_check:
                    # Hash for local storage
                    data = file_to_check.read()
                    md5 = hashlib.md5(data.encode('utf-8')).digest()
                    print('MD5 of {} is {} '.format(file, md5))

                if file_same_as_bucket_file():
                    print('Ignoring file {} because it has not changed'.format(file))
                else:
                    print('Uploading {} to bucket {}'.format(file, bucket_name))
                    upload_blob(bucket_name=bucket_name,
                                source_file_name=file,
                                destination_blob_name=survey_destination_path + file)
    except Exception as err:
        print('Connection error:', err)
        raise

    return


def file_same_as_bucket_file():
    # Function to compare hashes
    return False


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    if blob.exists():
        blob2 = bucket.get_blob('OPN/opn1911a/opn1911a.manifest')
        print('MD5 in bucket: ', pybase64.b64decode(blob2.md5_hash))
        print('Replacing with new version of {}.'.format(
            destination_blob_name))
    else:
        print('Creating new file {}.'.format(
            destination_blob_name))

    blob.upload_from_filename(source_file_name)
    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))
    return


if __name__ == "__main__":
    main()

