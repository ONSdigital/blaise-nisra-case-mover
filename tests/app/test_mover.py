from flask import Flask

from app.mover import config_loader


def test_config_loader_immutability(config, sftp_config):
    test_app = Flask("test_app")
    test_app.nisra_config = config
    test_app.sftp_config = sftp_config
    nisra_config, actual_sftp_config = config_loader(test_app)
    assert nisra_config.bucket_name == "env_var_not_set"
    assert actual_sftp_config.survey_source_path == "./ONS/OPN"
    test_app.nisra_config.bucket_name = "foobar"
    test_app.sftp_config.survey_source_path = "break_this"
    assert nisra_config.bucket_name == "env_var_not_set"
    assert actual_sftp_config.survey_source_path == "./ONS/OPN"
