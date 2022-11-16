import logging

from services.nisra_update_check_service import NisraUpdateCheckService


def nisra_changes_checker(nisra_update_check_service: NisraUpdateCheckService) -> str:
    logging.info("Starting Nisra check cloud function")
    return nisra_update_check_service.check_nisra_files_have_updated()
