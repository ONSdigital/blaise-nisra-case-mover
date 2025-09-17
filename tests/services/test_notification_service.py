import logging
from unittest import mock

import pytest
from notifications_python_client import NotificationsAPIClient

from models.configuration.notification_config_model import NotificationConfig
from services.notification_service import NotificationService


@pytest.fixture()
def config() -> NotificationConfig:
    return NotificationConfig(
        notify_api_key="94264180-7ebd-4ff9-8a27-52abb5949c78-94264180-7ebd-4ff9-8a27-52abb5949c78",
        nisra_notify_email="notify@ons.gov.uk",
    )


@pytest.fixture()
def notification_service(config: NotificationConfig) -> NotificationService:
    return NotificationService(config=config)


@mock.patch.object(NotificationsAPIClient, "send_email_notification")
def test_send_email_notification_calls_the_notification_client_with_the_correct_parameters(
    _mock_notification_client, notification_service
):
    # arrange
    message = {"questionnaire_name": "LMS2202_AA1"}
    template_id = "94264180-7ebd-4ff9-8a27-52abb5949c78"

    # act
    notification_service.send_email_notification(message, template_id)

    # assert
    _mock_notification_client.assert_called_with(
        email_address="notify@ons.gov.uk",
        template_id="94264180-7ebd-4ff9-8a27-52abb5949c78",
        personalisation={"questionnaire_name": "LMS2202_AA1"},
    )


@mock.patch.object(NotificationsAPIClient, "send_email_notification")
def test_send_email_notification_logs_an_error_if_exception_occurs(
    _mock_notification_client, notification_service, caplog
):
    # arrange
    message = {"questionnaire_name": "LMS2202_AA1"}
    template_id = "94264180-7ebd-4ff9-8a27-52abb5949c78"
    _mock_notification_client.side_effect = Exception()

    # act
    with pytest.raises(Exception):
        with caplog.at_level(logging.ERROR):
            notification_service.send_email_notification(message, template_id)

    assert (
        "root",
        logging.ERROR,
        f"NotificationService: Error when sending email via GOV.UK Notify API - ",
    ) in caplog.record_tuples
