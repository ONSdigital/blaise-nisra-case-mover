import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from services.blaise_service import BlaiseService
from services.google_bucket_service import GoogleBucketService
from services.nisra_update_check_service import NisraUpdateCheckService
from services.notification_service import NotificationService


@pytest.fixture()
def mock_blaise_service():
    return Mock()


@pytest.fixture()
def mock_bucket_service():
    return Mock()


@pytest.fixture()
def mock_notification_service():
    return Mock()


@pytest.fixture()
def nisra_update_check_service(
    mock_blaise_service: BlaiseService,
    mock_bucket_service: GoogleBucketService,
    mock_notification_service: NotificationService,
) -> NisraUpdateCheckService:
    return NisraUpdateCheckService(
        blaise_service=mock_blaise_service,
        bucket_service=mock_bucket_service,
        notification_service=mock_notification_service,
    )


def test_check_nisra_files_returns_done(mock_blaise_service, nisra_update_check_service):

    # arrange
    mock_blaise_service.get_names_of_questionnaire_in_blaise.return_value = []

    # act
    result = nisra_update_check_service.check_nisra_files_have_updated()

    # assert
    assert result == "Done"


def test_check_nisra_files_have_updated_calls_the_blaise_service_with_correct_survey_type(mock_blaise_service, nisra_update_check_service):

    # arrange
    mock_blaise_service.get_names_of_questionnaire_in_blaise.return_value = []

    # act
    nisra_update_check_service.check_nisra_files_have_updated()

    # assert
    mock_blaise_service.get_names_of_questionnaire_in_blaise.assert_called_with("LM")


def test_check_nisra_files_sends_a_notification_if_a_file_has_not_been_updated_for_23_hours(
    mock_blaise_service,
    mock_bucket_service,
    mock_notification_service,
    nisra_update_check_service,
):

    # arrange
    mock_blaise_service.get_names_of_questionnaire_in_blaise.return_value = [
        "LMS2201_AA1",
        "LMS2301_AB1",
    ]

    datetime_now = datetime.now(timezone.utc)
    mock_bucket_service.get_questionnaire_modified_dates.return_value = {
        "LMS2201_AA1": datetime_now - timedelta(hours=23, minutes=30),
        "LMS2301_AB1": datetime_now - timedelta(hours=15, minutes=0),
    }

    # act
    nisra_update_check_service.check_nisra_files_have_updated()

    # assert
    mock_notification_service.send_email_notification.assert_called_once()
    mock_notification_service.send_email_notification.assert_called_with(
        message={"questionnaire_name": "LMS2201_AA1"},
        template_id="94264180-7ebd-4ff9-8a27-52abb5949c78",
    )


def test_check_nisra_files_sends_a_notification_if_an_active_instrument_is_missing_in_the_bucket(
    mock_blaise_service,
    mock_bucket_service,
    mock_notification_service,
    nisra_update_check_service,
    caplog,
):

    # arrange
    mock_blaise_service.get_names_of_questionnaire_in_blaise.return_value = [
        "LMS2201_AA1",
        "LMS2301_AB1",
    ]

    datetime_now = datetime.now(timezone.utc)
    mock_bucket_service.get_questionnaire_modified_dates.return_value = {
        "LMS2301_AB1": datetime_now - timedelta(hours=1, minutes=0),
    }

    # act
    with caplog.at_level(logging.WARNING):
        nisra_update_check_service.check_nisra_files_have_updated()

    # assert
    mock_notification_service.send_email_notification.assert_called_once()
    mock_notification_service.send_email_notification.assert_called_with(
        message={"questionnaire_name": "LMS2201_AA1"},
        template_id="f9292929-8763-4147-ad1a-681398e8d9fc",
    )


def test_check_nisra_files_ignores_files_in_the_bucket_that_are_not_active_in_blaise(
    mock_blaise_service,
    mock_bucket_service,
    mock_notification_service,
    nisra_update_check_service,
):

    # arrange
    mock_blaise_service.get_names_of_questionnaire_in_blaise.return_value = [
        "LMS2201_AA1",
    ]

    datetime_now = datetime.now(timezone.utc)
    mock_bucket_service.get_questionnaire_modified_dates.return_value = {
        "LMS2201_AA1": datetime_now - timedelta(hours=23, minutes=30),
        "LMS2301_AB1": datetime_now - timedelta(hours=23, minutes=30),
    }

    # act
    nisra_update_check_service.check_nisra_files_have_updated()

    # assert
    mock_notification_service.send_email_notification.assert_called_once()
    mock_notification_service.send_email_notification.assert_called_with(
        message={"questionnaire_name": "LMS2201_AA1"},
        template_id="94264180-7ebd-4ff9-8a27-52abb5949c78",
    )
