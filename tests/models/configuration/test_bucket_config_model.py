import logging

from models.configuration.bucket_config_model import BucketConfig


def test_from_env_sets_properties_as_empty_strings_if_vars_are_not_available_from_env():
    # arrange & act
    config = BucketConfig.from_env()

    # assert
    assert config == BucketConfig(
        bucket_name="",
    )


def test_from_env_pulls_correct_vars_from_env(monkeypatch):
    # arrange & act
    monkeypatch.setenv("NISRA_BUCKET_NAME", "NISRA")
    config = BucketConfig.from_env()

    # assert
    assert config == BucketConfig(
        bucket_name="NISRA",
    )


def test_log_outputs_the_correct_vars_from_env(monkeypatch, caplog):
    # arrange & act
    monkeypatch.setenv("NISRA_BUCKET_NAME", "NISRA")
    config = BucketConfig.from_env()

    # act
    with caplog.at_level(logging.INFO):
        config.log()

    # assert
    assert (
        "root",
        logging.INFO,
        f"bucket_name: NISRA",
    ) in caplog.record_tuples
