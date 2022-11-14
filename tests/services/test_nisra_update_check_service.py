from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from services.nisra_update_check_service import NisraUpdateCheckService


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
        mock_blaise_service,
        mock_bucket_service,
        mock_notification_service) -> NisraUpdateCheckService:
    return NisraUpdateCheckService(
        blaise_service=mock_blaise_service,
        bucket_service=mock_bucket_service,
        notification_service=mock_notification_service
    )


def test_check_nisra_files_returns_done(
        mock_blaise_service,
        nisra_update_check_service):

    # arrange
    mock_blaise_service.get_names_of_questionnaire_in_blaise.return_value = []

    # act
    result = nisra_update_check_service.check_nisra_files_have_updated()

    # assert
    assert result == "Done"


def test_check_nisra_files_have_updated_calls_the_blaise_service_with_correct_survey_type(
        mock_blaise_service,
        nisra_update_check_service):

    # arrange
    mock_blaise_service.get_names_of_questionnaire_in_blaise.return_value = []

    # act
    nisra_update_check_service.check_nisra_files_have_updated()

    # assert
    mock_blaise_service.get_names_of_questionnaire_in_blaise.assert_called_with("LMS")


def test_check_nisra_files_sends_a_notification_if_a_file_has_not_been_updated_for_23_hours(
        mock_blaise_service,
        mock_bucket_service,
        mock_notification_service,
        nisra_update_check_service):

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
    mock_notification_service.send_email_notification.assert_called_with("LMS2201_AA1")

