import logging
from unittest import mock

import pytest
from google.cloud.storage import Blob

from models.configuration.bucket_config_model import BucketConfig

from services.google_bucket_service import GoogleBucketService


@pytest.fixture()
def bucket_name() -> str:
    return "NISRA"


@pytest.fixture()
def config(bucket_name) -> BucketConfig:
    return BucketConfig(
        bucket_name=bucket_name
    )


@pytest.fixture()
def bucket_service(config) -> GoogleBucketService:
    return GoogleBucketService(config=config)


@mock.patch.object(GoogleBucketService, "get_blobs")
def test_get_questionnaire_modified_dates_returns_the_correct_instrument_file_names(
    mock_get_blobs, bucket_service, bucket_name
):
    # arrange
    file_extension = "bdbx"
    mock_get_blobs.return_value = [
        Blob(name="LMS2202_AA1/LMS2202_AA1.BMIX", bucket=bucket_name),
        Blob(name="LMS2202_AA1/LMS2202_AA1.BDBX", bucket=bucket_name),
        Blob(name="LMS2202_AA1/LMS2202_AA1.BDIX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BMIX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BDBX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BDIX", bucket=bucket_name),
        Blob(name="LMS2301_AB1/LMS2202_AA1.BMIX", bucket=bucket_name),
        Blob(name="LMS2301_AB1/LMS2202_AA1.BDBX", bucket=bucket_name),
        Blob(name="LMS2301_AB1/LMS2202_AA1.BDIX", bucket=bucket_name),
    ]

    # act
    result = bucket_service.get_questionnaire_modified_dates(file_extension)

    # assert
    assert "LMS2202_AA1" in result
    assert "OPN2101A" in result
    assert "LMS2301_AB1" in result


@mock.patch.object(GoogleBucketService, "get_blobs")
def test_get_questionnaire_modified_dates_returns_the_correct_instrument_file_names_irrespective_of_case(
    mock_get_blobs, bucket_service, bucket_name
):
    # arrange
    file_extension = "bdbx"
    mock_get_blobs.return_value = [
        Blob(name="LMS2202_AA1/LMS2202_AA1.BMIX", bucket=bucket_name),
        Blob(name="LMS2202_AA1/LMS2202_AA1.BDBX", bucket=bucket_name),
        Blob(name="LMS2302_AA1/LMS2202_AA1.BDIX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BMIX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BDBX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BDIX", bucket=bucket_name),
        Blob(name="lms2301_ab1/lms2301_ab1.bmix", bucket=bucket_name),
        Blob(name="lms2301_ab1/lms2301_ab1.bdbx", bucket=bucket_name),
        Blob(name="lms2301_ab1/lms2301_ab1.bdix", bucket=bucket_name),
    ]

    # act
    result = bucket_service.get_questionnaire_modified_dates(file_extension)

    # assert
    # assert
    assert "LMS2202_AA1" in result
    assert "OPN2101A" in result
    assert "LMS2301_AB1" in result


@mock.patch.object(GoogleBucketService, "get_blobs")
def test_get_questionnaire_modified_dates_returns_only_the_instrument_file_names_where_a_bdbx_exists(
    mock_get_blobs, bucket_service, bucket_name
):
    # arrange
    file_extension = "bdbx"
    mock_get_blobs.return_value = [
        Blob(name="LMS2202_AA1/LMS2202_AA1.BMIX", bucket=bucket_name),
        Blob(name="LMS2202_AA1/LMS2202_AA1.BDIX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BMIX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BDBX", bucket=bucket_name),
        Blob(name="OPN2101A/OPN2101A.BDIX", bucket=bucket_name),
        Blob(name="LMS2301_AB1/LMS2202_AA1.BMIX", bucket=bucket_name),
        Blob(name="LMS2301_AB1/LMS2202_AA1.BDBX", bucket=bucket_name),
        Blob(name="LMS2301_AB1/LMS2202_AA1.BDIX", bucket=bucket_name),
        Blob(name="DST3399/DST3399.BDBX", bucket=bucket_name),
    ]

    # act
    result = bucket_service.get_questionnaire_modified_dates(file_extension)

    # assert
    assert "OPN2101A" in result
    assert "LMS2301_AB1" in result
    assert "DST3399" in result


@mock.patch.object(GoogleBucketService, "get_blobs")
def test_get_questionnaire_modified_dates_logs_an_error_if_exception_occurs(
    mock_get_blobs, bucket_service, caplog
):
    # arrange
    file_extension = "bdbx"
    mock_get_blobs.side_effect = Exception()

    # act
    with caplog.at_level(logging.ERROR):
        bucket_service.get_questionnaire_modified_dates(file_extension)

    assert (
        "root",
        logging.ERROR,
       f"GoogleStorageService: error in calling 'get_files_from_bucket' - "
    ) in caplog.record_tuples

