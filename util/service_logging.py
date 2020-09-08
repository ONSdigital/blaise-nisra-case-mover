import logging.config
from os import path
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging


def __init():
    __logger = logging.getLogger(__name__)
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
    logging.config.fileConfig(fname=log_file_path, disable_existing_loggers=False)

    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client, name="BNCM")
    setup_logging(handler)
    return __logger


log = __init()
