
from models.configuration.check_nisra_update_config_model import NisraUpdateCheckConfig


def test_model_populates_expected_vars():
    # arrange & act
    config = NisraUpdateCheckConfig.from_env()

    # assert
    assert config == NisraUpdateCheckConfig(
        survey_type="LMS",
        bucket_file_type="bdbx",
        max_hours_since_last_update=23,
        no_update_template_id="94264180-7ebd-4ff9-8a27-52abb5949c78",
        missing_questionnaire_template_id="f9292929-8763-4147-ad1a-681398e8d9fc"
    )

