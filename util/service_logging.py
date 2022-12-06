from google.cloud.logging_v2.handlers import StructuredLogHandler, setup_logging


def setupLogging():
    setup_logging(StructuredLogHandler())
