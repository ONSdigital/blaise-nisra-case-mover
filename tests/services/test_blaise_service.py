import logging
from typing import Any, Dict, List
from unittest import mock

import blaise_restapi
import pytest
from urllib3.exceptions import HTTPError

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
def blaise_service(config: BlaiseConfig) -> BlaiseService:
    return BlaiseService(config=config)


@mock.patch.object(blaise_restapi.Client, "get_all_questionnaires_for_server_park")
def test_get_questionnaires_calls_the_rest_api_client_with_the_correct_parameters(
    _mock_rest_api_client, blaise_service, questionnaire_list
):
    # arrange
    _mock_rest_api_client.return_value = questionnaire_list

    # act
    blaise_service.get_questionnaires()

    # assert
    _mock_rest_api_client.assert_called_with("gusty")


@mock.patch.object(blaise_restapi.Client, "get_all_questionnaires_for_server_park")
def test_get_questionnaires_returns_a_list_of_questionnaires(
    _mock_rest_api_client,
    blaise_service,
):
    # arrange
    _mock_rest_api_client.return_value = questionnaire_list

    # act
    result = blaise_service.get_questionnaires()

    # assert
    assert result == questionnaire_list


@mock.patch.object(blaise_restapi.Client, "get_all_questionnaires_for_server_park")
def test_get_questionnaires_logs_an_error_if_exception_occurs(
    _mock_rest_api_client, blaise_service, caplog
):
    # arrange
    _mock_rest_api_client.side_effect = HTTPError()

    # act
    with pytest.raises(Exception):
        with caplog.at_level(logging.ERROR):
            blaise_service.get_questionnaires()

    assert (
        "root",
        logging.ERROR,
        "BlaiseService: error in calling 'get_all_questionnaires_for_server_park': ",
    ) in caplog.record_tuples


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
