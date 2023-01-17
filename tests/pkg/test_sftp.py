import logging
import os
import stat
from datetime import datetime
from unittest import mock

import pytest

from models.instruments import Instrument
from pkg.sftp import SFTP, SFTPConfig


@mock.patch.dict(
    os.environ,
    {
        "SFTP_HOST": "test_host",
        "SFTP_USERNAME": "test_username",
        "SFTP_PASSWORD": "test_password",
        "SFTP_PORT": "1234",
    },
)
def test_sftpconfig_from_env_gets_values_from_the_env():
    config = SFTPConfig.from_env()
    assert config.host == "test_host"
    assert config.username == "test_username"
    assert config.password == "test_password"
    assert config.port == "1234"


@mock.patch.dict(os.environ, {})
def test_sftpconfig_from_env_raises_when_env_vars_are_missing():
    with pytest.raises(
        Exception,
        match=(
            "The following required environment variables have not been set: "
            "SFTP_HOST, SFTP_USERNAME, SFTP_PASSWORD, SFTP_PORT"
        ),
    ):
        SFTPConfig.from_env()


def test_get_instrument_folders(
    mock_sftp_connection, sftp_config, config, mock_list_dir_attr
):
    mock_sftp_connection.listdir_attr.return_value = [
        mock_list_dir_attr(filename="OPN2101A", st_mtime=1, st_mode=stat.S_IFDIR),
        mock_list_dir_attr(filename="LMS2101A", st_mtime=1, st_mode=stat.S_IFDIR),
        mock_list_dir_attr(filename="lMS2101A", st_mtime=1, st_mode=stat.S_IFDIR),
        mock_list_dir_attr(filename="lMS2101a", st_mtime=1, st_mode=stat.S_IFDIR),
        mock_list_dir_attr(filename="lMS2101a.zip", st_mtime=1, st_mode=stat.S_IFREG),
        mock_list_dir_attr(filename="foobar", st_mtime=1, st_mode=stat.S_IFDIR),
    ]
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.get_instrument_folders("./ONS/OPN") == {
        "OPN2101A": Instrument(sftp_path="./ONS/OPN/OPN2101A"),
        "LMS2101A": Instrument(sftp_path="./ONS/OPN/LMS2101A"),
        "lMS2101A": Instrument(sftp_path="./ONS/OPN/lMS2101A"),
        "lMS2101a": Instrument(sftp_path="./ONS/OPN/lMS2101a"),
    }


def test_get_instrument_files(
    mock_sftp_connection, sftp_config, config, mock_list_dir_attr
):
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    instrument_folders = {"OPN2101A": Instrument(sftp_path="ONS/OPN/OPN2101A")}
    mock_sftp_connection.listdir_attr.return_value = [
        mock_list_dir_attr(filename="oPn2101A.BdBx", st_mtime=1617186113),
        mock_list_dir_attr(filename="oPn2101A.BdIx", st_mtime=1617186091),
        mock_list_dir_attr(filename="oPn2101A.BmIx", st_mtime=1617186113),
        mock_list_dir_attr(filename="oPn2101A.pdf", st_mtime=1617186117),
        mock_list_dir_attr(filename="FrameSOC.blix", st_mtime=1617186117),
    ]

    assert sftp.get_instrument_files(instrument_folders) == {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        )
    }


def test_filter_invalid_instrument_filenames_logs_an_error_when_instrument_files_are_misnamed(
    mock_sftp_connection, sftp_config, config, mock_list_dir_attr, caplog
):
    # arrange
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    instrument_folders = {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "2101A.BdIx",
                "oPn2101a.BmIx",
                "FrameSOC.blix",
                "sOc2023_xlib.BmIx",
            ],  # contains invalid filename
        ),
        "OPN2102A": Instrument(
            sftp_path="ONS/OPN/OPN2102A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2102A.BdBx",
                "oPn2102A.BdIx",
                "FrameSOC.blix",
            ],  # invalid number of required files
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2103a.BdBx",
                "oPn2103A.BdIx",
                "oPn2103a.BmIx",
                "FrameSOC.blix",
                "sOc2023_xlib.BmIx",
            ],  # completely valid
        ),
    }

    # act and assert
    with caplog.at_level(logging.ERROR):
        sftp.filter_invalid_instrument_filenames(instrument_folders)

    assert (
        "root",
        logging.ERROR,
        "Invalid filenames found in NISRA sftp for OPN2101A - not importing",
    ) in caplog.record_tuples
    assert (
        "root",
        logging.ERROR,
        "Invalid filenames found in NISRA sftp for OPN2102A - not importing",
    ) in caplog.record_tuples
    assert (
        not (
            "root",
            logging.ERROR,
            "Invalid filenames found in NISRA sftp for OPN2103A - not importing",
        )
        in caplog.record_tuples
    )


def test_filter_invalid_instrument_filenames_removes_instrument_with_invalid_files(
    mock_sftp_connection, sftp_config, config, mock_list_dir_attr, caplog
):
    # arrange
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    instrument_folders = {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "2101A.BdIx",
                "oPn2101a.BmIx",
                "FrameSOC.blix",
                "sOc2023_xlib.BmIx",
            ],  # contains invalid filename
        ),
        "OPN2102A": Instrument(
            sftp_path="ONS/OPN/OPN2102A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2102A.BdBx",
                "oPn2102A.BdIx",
                "FrameSOC.blix",
            ],  # invalid number of required files
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2103a.BdBx",
                "oPn2103A.BdIx",
                "oPn2103a.BmIx",
                "FrameSOC.blix",
                "sOc2023_xlib.BmIx",
            ],  # completely valid
        ),
    }

    # act and assert
    assert sftp.filter_invalid_instrument_filenames(instrument_folders) == {
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2103a.BdBx",
                "oPn2103A.BdIx",
                "oPn2103a.BmIx",
                "FrameSOC.blix",
                "sOc2023_xlib.BmIx",
            ],
        ),
    }


def test_filter_instrument_files_removes_instruments_without_bdbx_files(
    mock_sftp_connection, sftp_config, config
):
    instrument_folders = {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2102A": Instrument(
            sftp_path="ONS/OPN/OPN2102A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2102A.BdIx",
                "oPn2102A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.filter_instrument_files(instrument_folders) == {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }


def test_filter_instrument_files_returns_the_latest_modified_when_names_clash(
    mock_sftp_connection, sftp_config, config
):
    instrument_folders = {
        "OPN2101A": Instrument(
            sftp_path="ONS/OPN/OPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "oPN2101A": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OpN2101A": Instrument(
            sftp_path="ONS/OPN/OpN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-03-31T11:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.filter_instrument_files(instrument_folders) == {
        "opn2101a": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }


@mock.patch.object(SFTP, "generate_bdbx_md5", return_value="my_lovely_md5")
def test_get_bdbx_md5s(
    mock_generate_bdbx_md5, mock_sftp_connection, sftp_config, config
):
    instruments = {
        "opn2101a": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    assert sftp.generate_bdbx_md5s(instruments) == {
        "opn2101a": Instrument(
            sftp_path="ONS/OPN/oPN2101A",
            bdbx_updated_at=datetime.fromisoformat("2021-04-30T10:21:53+00:00"),
            bdbx_md5="my_lovely_md5",
            files=[
                "oPn2101A.BdBx",
                "oPn2101A.BdIx",
                "oPn2101A.BmIx",
                "FrameSOC.blix",
            ],
        ),
        "OPN2103A": Instrument(
            sftp_path="ONS/OPN/OPN2103A",
            bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
            bdbx_md5="my_lovely_md5",
            files=[
                "oPn2103A.BdBx",
            ],
        ),
    }
    assert mock_generate_bdbx_md5.call_count == 2


def test_generate_bdbx_md5(
    mock_sftp_connection, sftp_config, config, mock_stat, fake_sftp_file
):
    fake_file = fake_sftp_file(b"My fake bdbx file")
    mock_sftp_connection.stat.return_value = mock_stat(st_size=17)
    mock_sftp_connection.open.return_value = fake_file
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "opn2103a.bdbx",
        ],
    )
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    # The md5 value for the fake file
    assert sftp.generate_bdbx_md5(instrument) == "50cc5a0bbd05754f98022a25566220fe"
    mock_sftp_connection.stat.assert_called_with("ONS/OPN/OPN2103A/opn2103a.bdbx")


def test_generate_bdbx_md5_when_file_does_not_exist(
    mock_sftp_connection, sftp_config, config, mock_stat, fake_sftp_file, caplog
):
    mock_sftp_connection.stat.return_value = mock_stat(st_size=17)
    mock_sftp_connection.open.side_effect = FileNotFoundError
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "opn2103a.bdbx",
        ],
    )
    sftp = SFTP(mock_sftp_connection, sftp_config, config)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(FileNotFoundError):
            sftp.generate_bdbx_md5(instrument)

    assert (
        "root",
        logging.ERROR,
        "Failed to open ONS/OPN/OPN2103A/opn2103a.bdbx over SFTP",
    ) in caplog.record_tuples
