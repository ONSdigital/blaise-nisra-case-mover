import logging
from typing import Any, Dict, List

import blaise_restapi

from models.configuration.blaise_config_model import BlaiseConfig


class BlaiseService:
    def __init__(self, config: BlaiseConfig):
        self._config = config
        self.restapi_client = blaise_restapi.Client(f"http://{self._config.blaise_api_url}")

    def get_questionnaires(self) -> List[Dict[str, Any]]:
        try:
            return self.restapi_client.get_all_questionnaires_for_server_park(self._config.server_park)
        except Exception as error:
            logging.error(f"BlaiseService: error in calling 'get_all_questionnaires_for_server_park': {error}")
            raise error

    def get_names_of_questionnaire_in_blaise(self, survey_type: str) -> List[str]:
        questionnaire_names = []
        questionnaires = self.get_questionnaires()
        for questionnaire in questionnaires:
            if not questionnaire["name"].upper().startswith(survey_type):
                logging.info(f"instrument name {questionnaire['name']} not supported")
                continue

            questionnaire_names.append(questionnaire["name"].upper())
            logging.info(f"instrument name {questionnaire['name']} added")

        return questionnaire_names
