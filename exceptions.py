import logging


class Error(Exception):
    """Base class for other exceptions"""


class TriggerError(Error):
    """Raised when the trigger cloud function fails"""
    logging.error(f"Trigger failed due to a an Exception. {Error}")


class ProcessorError(Error):
    """Raised when the processor cloud function fails"""
    logging.error(f"Processor failed due to a an Exception. {Error}")
