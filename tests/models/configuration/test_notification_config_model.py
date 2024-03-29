import logging

from models.configuration.notification_config_model import NotificationConfig


def test_from_env_sets_properties_as_empty_strings_if_vars_are_not_available_from_env():
    # arrange & act
    config = NotificationConfig.from_env()

    # assert
    assert config == NotificationConfig(
        notify_api_key="",
        nisra_notify_email="",
    )


def test_from_env_pulls_correct_vars_from_env(monkeypatch):
    # arrange & act
    monkeypatch.setenv("NOTIFY_API_KEY", "AE88HF98")
    monkeypatch.setenv("NISRA_NOTIFY_EMAIL", "notify@ons.gov.uk")
    config = NotificationConfig.from_env()

    # assert
    assert config == NotificationConfig(
        notify_api_key="AE88HF98",
        nisra_notify_email="notify@ons.gov.uk",
    )


def test_log_outputs_the_correct_vars_from_env(monkeypatch, caplog):
    # arrange & act
    monkeypatch.setenv("NOTIFY_API_KEY", "AE88HF98")
    monkeypatch.setenv("NISRA_NOTIFY_EMAIL", "notify@ons.gov.uk")
    config = NotificationConfig.from_env()

    # act
    with caplog.at_level(logging.INFO):
        config.log()

    # assert
    assert (
        "root",
        logging.INFO,
        f"notify_api_key: AE88HF98",
    ) in caplog.record_tuples

    assert (
        "root",
        logging.INFO,
        f"nisra_notify_email: notify@ons.gov.uk",
    ) in caplog.record_tuples
