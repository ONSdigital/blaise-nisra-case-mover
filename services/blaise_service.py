from typing import List, Dict, Any

import blaise_restapi

from models.configuration.blaise_config_model import BlaiseConfig


class BlaiseService:
    def __init__(self, config: BlaiseConfig):
        self._config = config
        self.restapi_client = blaise_restapi.Client(self._config.blaise_api_url)

    def get_instruments(self) -> List[Dict[str, Any]]:
        return self.restapi_client.get_all_questionnaires_for_server_park(self._config.server_park)