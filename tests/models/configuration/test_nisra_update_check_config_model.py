from models.configuration.check_nisra_update_config_model import NisraUpdateCheckConfig


def test_model_populates_expected_vars():
    # arrange & act
    config = NisraUpdateCheckConfig()

    # assert
    assert config.survey_type == "LMS"
    assert config.bucket_file_type == "bdbx"
    assert config.max_hours_since_last_update == 23
    assert config.no_update_template_id == "94264180-7ebd-4ff9-8a27-52abb5949c78"
    assert (
        config.missing_questionnaire_template_id
        == "f9292929-8763-4147-ad1a-681398e8d9fc"
    )
