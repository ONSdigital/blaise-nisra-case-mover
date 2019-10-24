import pysftp
import os
import logging


def establish_sftp_connection():
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(os.getenv('SFTP_HOST'), username=os.getenv('SFTP_USERNAME'), password=os.getenv('SFTP_PASSWORD'), port=int(os.getenv('SFTP_PORT')), cnopts=cnopts)
    except Exception as err:
        print('Connection error:', err)
        raise

    return sftp


def look_for_survey_folder(sftp):

    return sftp.listdir('ONS')


sftp = establish_sftp_connection()
logging.log('INFO', look_for_survey_folder(sftp))

# def get_all_blaise_files(sftp):
