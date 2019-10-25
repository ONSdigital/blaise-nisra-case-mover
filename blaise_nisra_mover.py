import pysftp
import os


def establish_sftp_connection():
    try:
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(os.getenv('SFTP_HOST'), username=os.getenv('SFTP_USERNAME'), password=os.getenv('SFTP_PASSWORD'), port=int(os.getenv('SFTP_PORT')), cnopts=cnopts)
        print(sftp.listdir('ONS'))
    except Exception as err:
        print('Connection error:', err)
        raise

    return sftp


sftp = establish_sftp_connection()
print('This is working')
exit(0)