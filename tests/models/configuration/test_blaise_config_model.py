import logging

from models.configuration.blaise_config_model import BlaiseConfig


def test_from_env_sets_properties_as_empty_strings_if_vars_are_not_available_from_env():
    # arrange & act
    config = BlaiseConfig.from_env()

    # assert
    assert config == BlaiseConfig(
        blaise_api_url="",
        server_park="",
    )


def test_from_env_pulls_correct_vars_from_env(monkeypatch):
    # arrange & act
    monkeypatch.setenv("BLAISE_API_URL", "http://localhost:90")
    monkeypatch.setenv("SERVER_PARK", "gusty")
    config = BlaiseConfig.from_env()

    # assert
    assert config == BlaiseConfig(
        blaise_api_url="http://localhost:90",
        server_park="gusty",
    )


def test_log_outputs_the_correct_vars_from_env(monkeypatch, caplog):
    # arrange & act
    monkeypatch.setenv("BLAISE_API_URL", "http://localhost:90")
    monkeypatch.setenv("SERVER_PARK", "gusty")
    config = BlaiseConfig.from_env()

    # act
    with caplog.at_level(logging.INFO):
        config.log()

    # assert
    assert (
        "root",
        logging.INFO,
        f"blaise_api_url: http://localhost:90",
    ) in caplog.record_tuples

    assert (
        "root",
        logging.INFO,
        f"server_park: gusty",
    ) in caplog.record_tuples
