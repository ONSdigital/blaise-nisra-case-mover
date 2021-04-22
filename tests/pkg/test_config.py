import logging
import os
from unittest import mock

from pkg.config import Config


@mock.patch.dict(
    os.environ,
    {
        "SERVER_PARK": "server_park_foobar",
        "BLAISE_API_URL": "blaise_api_url_haha",
        "NISRA_BUCKET_NAME": "nisra_bucket",
    },
)
def test_config_from_env():
    config = Config.from_env()
    assert config.server_park == "server_park_foobar"
    assert config.blaise_api_url == "blaise_api_url_haha"
    assert config.bucket_name == "nisra_bucket"


def test_config_log(caplog):
    config = Config()
    config.log()
    assert caplog.record_tuples == [
        ("util.service_logging", logging.INFO, "bucket_name - env_var_not_set"),
        (
            "util.service_logging",
            logging.INFO,
            "instrument_regex - ^[a-zA-Z]{3}[0-9][0-9][0-9][0-9]",
        ),
        (
            "util.service_logging",
            logging.INFO,
            "extension_list - ['.blix', '.bdbx', '.bdix', '.bmix']",
        ),
        ("util.service_logging", logging.INFO, "server_park - env_var_not_set"),
        ("util.service_logging", logging.INFO, "blaise_api_url - env_var_not_set"),
    ]
