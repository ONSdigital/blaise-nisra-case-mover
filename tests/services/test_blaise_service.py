from typing import List, Dict, Any
from unittest import mock

import blaise_restapi
import pytest

from models.configuration.blaise_config_model import BlaiseConfig
from services.blaise_service import BlaiseService


@pytest.fixture()
def questionnaire_list() -> List[Dict[str, Any]]:
    return [
        {
            "name": "LMS2202_AA1",
            "id": "12345-12345-12345-12345-XXXXX",
            "serverParkName": "gusty",
        },
        {
            "name": "OPN2101A",
            "id": "12345-12345-12345-12345-ZZZZZ",
            "serverParkName": "gusty",
        },
        {
            "name": "DST2106Y",
            "id": "12345-12345-12345-12345-YYYYY",
            "serverParkName": "gusty",
        },
        {
            "name": "LMS2201_AB1",
            "id": "12345-12345-12345-12345-VVVVV",
            "serverParkName": "gusty",
        },
    ]


@pytest.fixture()
def config() -> BlaiseConfig:
    return BlaiseConfig(
        blaise_api_url="http://localhost:90",
        server_park="gusty",
    )


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@mock.patch.object(blaise_restapi.Client, "get_all_questionnaires_for_server_park")
def test_get_questionnaires_calls_the_rest_api_client_with_the_correct_parameters(
    _mock_rest_api_client, blaise_service, questionnaire_list
):
    # arrange
    _mock_rest_api_client.return_value = questionnaire_list

    # act
    result = blaise_service.get_questionnaires()

    # assert
    result = questionnaire_list


@mock.patch.object(blaise_restapi.Client, "get_all_questionnaires_for_server_park")
def test_get_questionnaires_returns_a_list_of_questionnaires(
    _mock_rest_api_client, blaise_service,
):
    # act
    blaise_service.get_questionnaires()

    # assert
    _mock_rest_api_client.assert_called_with("gusty")


@mock.patch.object(blaise_restapi.Client, "get_all_questionnaires_for_server_park")
def test_get_names_of_questionnaire_in_blaise_returns_the_expected_names_for_survey_types(
    _mock_rest_api_client, blaise_service, questionnaire_list
):
    # arrange
    _mock_rest_api_client.return_value = questionnaire_list
    survey_type = "LMS"

    # act
    result = blaise_service.get_names_of_questionnaire_in_blaise(survey_type)

    # assert
    assert result == ["LMS2202_AA1", "LMS2201_AB1"]