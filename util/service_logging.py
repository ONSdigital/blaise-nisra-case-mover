import json
import logging
import logging.config
import sys


class CloudLoggingFormatter(logging.Formatter):
    """Produces messages compatible with google cloud logging"""

    def format(self, record: logging.LogRecord) -> str:
        s = super().format(record)
        return json.dumps(
            {
                "message": s,
                "severity": record.levelname,
                "timestamp": {"seconds": int(record.created), "nanos": 0},
            }
        )


def setupLogging() -> logging.Logger:
    root = logging.getLogger()
    if not len(root.handlers):
        handler = logging.StreamHandler(sys.stdout)
        formatter = CloudLoggingFormatter(fmt="[%(name)s] %(message)s")
        handler.setFormatter(formatter)
        root.addHandler(handler)
        root.setLevel(logging.INFO)
    return root
