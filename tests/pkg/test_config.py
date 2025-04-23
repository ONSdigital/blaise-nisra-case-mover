import logging
import os
from unittest import mock

import pytest

from pkg.config import Config
from util.service_logging import setupLogging


@mock.patch.dict(
    os.environ,
    {
        "SERVER_PARK": "server_park_foobar",
        "BLAISE_API_URL": "blaise_api_url_haha",
        "NISRA_BUCKET_NAME": "nisra_bucket",
        "PROJECT_ID": "project_id",
        "PROCESSOR_TOPIC_NAME": "processor_topic_name",
    },
)
def test_config_from_env():
    config = Config.from_env()
    assert config.server_park == "server_park_foobar"
    assert config.blaise_api_url == "blaise_api_url_haha"
    assert config.bucket_name == "nisra_bucket"
    assert config.project_id == "project_id"
    assert config.processor_topic_name == "processor_topic_name"


@mock.patch.dict(os.environ, {})
def test_raises_when_env_vars_are_missing():
    with pytest.raises(
        Exception,
        match=(
            "The following required environment variables have not been set: "
            "SERVER_PARK, BLAISE_API_URL, NISRA_BUCKET_NAME, PROJECT_ID, "
            "PROCESSOR_TOPIC_NAME"
        ),
    ):
        Config.from_env()


@mock.patch.dict(
    os.environ,
    {
        "SERVER_PARK": "server_park_foobar",
        "BLAISE_API_URL": "blaise_api_url_haha",
        "NISRA_BUCKET_NAME": "nisra_bucket",
        "PROJECT_ID": "project_id",
        "PROCESSOR_TOPIC_NAME": "processor_topic_name",
    },
)
def test_config_log(caplog):
    caplog.set_level(logging.INFO)
    setupLogging()
    config = Config.from_env()
    config.log()
    assert caplog.record_tuples == [
        ("root", logging.INFO, "bucket_name - nisra_bucket"),
        (
            "root",
            logging.INFO,
            "{'logging.googleapis.com/diagnostic': {'instrumentation_source': [{'name': "
            "'python', 'version': '3.3.1'}]}}",
        ),
        (
            "root",
            logging.INFO,
            "valid_surveys - ['OPN', 'LMS', 'LMX']",
        ),
        (
            "root",
            logging.INFO,
            "extension_list - ['.blix', '.bdbx', '.bdix', '.bmix']",
        ),
        ("root", logging.INFO, "server_park - server_park_foobar"),
        ("root", logging.INFO, "blaise_api_url - blaise_api_url_haha"),
        ("root", logging.INFO, "project_id - project_id"),
        (
            "root",
            logging.INFO,
            "processor_topic_name - processor_topic_name",
        ),
    ]


@pytest.mark.parametrize(
    "survey_name,expected",
    [
        ("OPN2101A", True),
        ("LMS2101A", True),
        ("LMS2101_DD3", True),
        ("LMS2101_DD3", True),
        ("lmsstudycontract", False),
        ("studycontract", False),
        ("lms2101_dd3", True),
        ("lmc2101_dd3", False),
        ("LMC2101_DD3", False),
        ("LMC21", False),
        ("LMS21", False),
    ],
)
def test_valid_survey_name(survey_name, expected):
    config = Config(
        bucket_name="test_bucket_name",
        server_park="test_server_park",
        blaise_api_url="test_blaise_api_url",
        project_id="test_project_id",
        processor_topic_name="test_processor_topic_name",
    )
    assert config.valid_survey_name(survey_name) == expected
