import hashlib
import math
import operator
import os
import pathlib
import stat
from datetime import datetime, timezone
from typing import Dict, List

import pysftp

from models import Instrument
from pkg.config import Config
import logging


class SFTPConfig:
    host = None
    username = None
    password = None
    port = None
    survey_source_path = None

    @classmethod
    def from_env(cls):
        cls.host = os.getenv("SFTP_HOST", "env_var_not_set")
        cls.username = os.getenv("SFTP_USERNAME", "env_var_not_set")
        cls.password = os.getenv("SFTP_PASSWORD", "env_var_not_set")
        cls.port = os.getenv("SFTP_PORT", "env_var_not_set")
        cls.survey_source_path = os.getenv("SURVEY_SOURCE_PATH", "env_var_not_set")
        return cls()

    def log(self):
        logging.info(f"survey_source_path - {self.survey_source_path}")
        logging.info(f"sftp_host - {self.host}")
        logging.info(f"sftp_port - {self.port}")
        logging.info(f"sftp_username - {self.username}")


class SFTP:
    def __init__(
        self,
        sftp_connection: pysftp.Connection,
        sftp_config: SFTPConfig,
        config: Config,
    ) -> None:
        self.sftp_connection = sftp_connection
        self.sftp_config = sftp_config
        self.config = config

    def get_instrument_folders(self) -> Dict[str, Instrument]:
        instruments = {}
        for folder_attr in self.sftp_connection.listdir_attr(
            self.sftp_config.survey_source_path
        ):
            if not stat.S_ISDIR(folder_attr.st_mode):
                continue
            folder = folder_attr.filename
            if self.config.valid_survey_name(folder):
                logging.info(f"Instrument folder found - {folder}")
                instruments[folder] = Instrument(
                    sftp_path=f"{self.sftp_config.survey_source_path}/{folder}"
                )
        return instruments

    def get_instrument_files(
        self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        for _, instrument in instruments.items():
            instrument.files = self._get_instrument_files_for_instrument(instrument)
        return instruments

    def filter_instrument_files(
        self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        filtered_instruments = self._filter_non_bdbx(instruments)
        confilcting_instruments = self._get_conflicting_instruments(
            filtered_instruments
        )
        return self._resolve_conflicts(filtered_instruments, confilcting_instruments)

    def generate_bdbx_md5s(
        self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        for _, instrument in instruments.items():
            instrument.bdbx_md5 = self.generate_bdbx_md5(instrument)
        return instruments

    def generate_bdbx_md5(self, instrument: Instrument) -> str:
        bdbx_file = instrument.bdbx_file()
        if not bdbx_file:
            log.info(
                f"No bdbx file for '{instrument.sftp_path}' cannot generate an md5"
            )
            return ""
        bdbx_details = self.sftp_connection.stat(bdbx_file)
        md5sum = hashlib.md5()
        chunks = math.ceil(bdbx_details.st_size / self.config.bufsize)
        sftp_file = self.sftp_connection.open(bdbx_file, bufsize=self.config.bufsize)
        sftp_file.prefetch()
        for chunk in range(chunks):
            sftp_file.seek(chunk * self.config.bufsize)
            md5sum.update(sftp_file.read(self.config.bufsize))
        return md5sum.hexdigest()

    def _get_instrument_files_for_instrument(self, instrument: Instrument) -> List[str]:
        instrument_file_list = []
        for instrument_file in self.sftp_connection.listdir_attr(instrument.sftp_path):
            file_extension = pathlib.Path(instrument_file.filename).suffix.lower()
            if file_extension == ".bdbx":
                instrument.bdbx_updated_at = datetime.fromtimestamp(
                    instrument_file.st_mtime, tz=timezone.utc
                )
            if file_extension in self.config.extension_list:
                logging.info(f"Instrument file found - {instrument_file.filename}")
                instrument_file_list.append(instrument_file.filename)
        return instrument_file_list

    def _resolve_conflicts(
        self,
        instruments: Dict[str, Instrument],
        confilcting_instruments: Dict[str, List[str]],
    ) -> Dict[str, Instrument]:
        filtered_instruments = {}
        processed_conflicts = []
        for instrument_name, instrument in instruments.items():
            if instrument_name.lower() in confilcting_instruments:
                if instrument_name in processed_conflicts:
                    continue
                filtered_instruments[
                    instrument_name.lower()
                ] = self._get_latest_conflicting_instrument(
                    instruments, confilcting_instruments, instrument_name
                )
                processed_conflicts += confilcting_instruments[instrument_name.lower()]
            else:
                filtered_instruments[instrument_name] = instrument
        return filtered_instruments

    def _filter_non_bdbx(
        _self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        filtered_instruments = {}
        for instrument_name, instrument in instruments.items():
            file_types = [
                pathlib.Path(file).suffix.lower() for file in instrument.files
            ]
            if ".bdbx" in file_types:
                filtered_instruments[instrument_name] = instrument
            else:
                logging.info(
                    "Instrument database file not found - "
                    + f"{instrument_name} - not importing"
                )
        return filtered_instruments

    def _get_conflicting_instruments(
        _self, instruments: Dict[str, Instrument]
    ) -> Dict[str, List[str]]:
        conflicting_instruments: Dict[str, List[str]] = {}
        for folder_name in instruments.keys():
            conflict_key = folder_name.lower()
            if conflict_key not in conflicting_instruments:
                conflicting_instruments[conflict_key] = []
            conflicting_instruments[conflict_key].append(folder_name)
        return {
            conflict_key: conflicting_instruments[conflict_key]
            for conflict_key, instruments in conflicting_instruments.items()
            if len(instruments) > 1
        }

    def _get_latest_conflicting_instrument(
        _self,
        instruments: Dict[str, Instrument],
        confilcting_instruments: Dict[str, List[str]],
        instrument_name: str,
    ) -> Instrument:
        conflict_instruments = confilcting_instruments[instrument_name.lower()]
        instrument_conflicts = {
            instrument_name: instruments[instrument_name]
            for instrument_name in conflict_instruments
        }
        sorted_conflicts = sorted(
            [instrument for _, instrument in instrument_conflicts.items()],
            key=operator.attrgetter("bdbx_updated_at"),
            reverse=True,
        )
        latest_instrument = sorted_conflicts[0]
        for conflict in sorted_conflicts[1:]:
            logging.info(
                f"Found newer instrument '{latest_instrument.sftp_path}' "
                + f"folder - Skipping this folder '{conflict.sftp_path}'"
            )
        return latest_instrument
