import hashlib
import logging
import math
import operator
import os
import pathlib
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Type, TypeVar

import pysftp

from models import Instrument
from pkg.config import Config

T = TypeVar("T", bound="SFTPConfig")


class InvalidFilenameError(Exception):
    pass


@dataclass
class SFTPConfig:
    host: str
    username: str
    password: str
    port: str

    @classmethod
    def from_env(cls: Type[T]) -> T:
        missing = []

        def get_from_env(name: str) -> str:
            try:
                return os.environ[name]
            except KeyError:
                missing.append(name)
                return ""

        instance = cls(
            host=get_from_env("SFTP_HOST"),
            username=get_from_env("SFTP_USERNAME"),
            password=get_from_env("SFTP_PASSWORD"),
            port=get_from_env("SFTP_PORT"),
        )

        if missing:
            raise Exception(
                "The following required environment variables have not been set: "
                + ", ".join(missing)
            )

        return instance

    def log(self):
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

    def get_instrument_folders(self, survey_source_path: str) -> Dict[str, Instrument]:
        instruments = {}
        for folder_attr in self.sftp_connection.listdir_attr(survey_source_path):
            if not stat.S_ISDIR(folder_attr.st_mode):
                continue
            folder = folder_attr.filename
            if self.config.valid_survey_name(folder):
                logging.info(f"Instrument folder found - {folder}")
                instruments[folder] = Instrument(
                    sftp_path=f"{survey_source_path}/{folder}"
                )
        return instruments

    def get_instrument_files(
        self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        for _, instrument in instruments.items():
            instrument.files = self._get_instrument_files_for_instrument(instrument)
        return instruments

    def filter_invalid_instrument_filenames(
        self, instruments: Dict[str, Instrument]
    ) -> None:
        for questionnaire_name, questionnaire in instruments.items():
            for file in questionnaire.files:
                filename = file.split(".")[0].lower()
                extension = file.split(".")[1].lower()

                if extension != "blix" and filename != questionnaire_name.lower():
                    logging.error(
                        f"Invalid filename {file} found in NISRA sftp for {questionnaire_name}. Filename should be {questionnaire_name}.{extension}. Please notify NISRA"
                    )

    def filter_instrument_files(
        self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        filtered_instruments = self._filter_non_bdbx(instruments)
        conflicting_instruments = self._get_conflicting_instruments(
            filtered_instruments
        )
        return self._resolve_conflicts(filtered_instruments, conflicting_instruments)

    def generate_bdbx_md5s(
        self, instruments: Dict[str, Instrument]
    ) -> Dict[str, Instrument]:
        for _, instrument in instruments.items():
            instrument.bdbx_md5 = self.generate_bdbx_md5(instrument)
        return instruments

    def generate_bdbx_md5(self, instrument: Instrument) -> str:
        bdbx_file = instrument.bdbx_file()
        if not bdbx_file:
            logging.info(
                f"No bdbx file for '{instrument.sftp_path}' cannot generate an md5"
            )
            return ""
        bdbx_details = self.sftp_connection.stat(bdbx_file)
        md5sum = hashlib.md5()
        chunks = math.ceil(bdbx_details.st_size / self.config.bufsize)
        try:
            sftp_file = self.sftp_connection.open(
                bdbx_file, bufsize=self.config.bufsize
            )
        except FileNotFoundError as error:
            logging.error(f"Failed to open {bdbx_file} over SFTP")
            raise error

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
        conflicting_instruments: Dict[str, List[str]],
    ) -> Dict[str, Instrument]:
        filtered_instruments = {}
        processed_conflicts = []
        for instrument_name, instrument in instruments.items():
            if instrument_name.lower() in conflicting_instruments:
                if instrument_name in processed_conflicts:
                    continue
                filtered_instruments[
                    instrument_name.lower()
                ] = self._get_latest_conflicting_instrument(
                    instruments, conflicting_instruments, instrument_name
                )
                processed_conflicts += conflicting_instruments[instrument_name.lower()]
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
        conflicting_instruments: Dict[str, List[str]],
        instrument_name: str,
    ) -> Instrument:
        conflict_instruments = conflicting_instruments[instrument_name.lower()]
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
