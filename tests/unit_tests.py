from unittest import mock
from unittest.mock import patch

import pytest

from blaise_nisra_case_mover import *


@pytest.fixture
def mock_sftp():
    return mock.MagicMock()


def test_get_instrument_folders(mock_sftp):
    mock_sftp.listdir.return_value = ["OPN2101A",
                                      "LMS2101A",
                                      "foobar"]
    assert get_instrument_folders(mock_sftp, "") == ["OPN2101A",
                                                     "LMS2101A"]


def test_get_instrument_files(mock_sftp):
    mock_sftp.listdir.return_value = ["OPN2101A.bdbx",
                                      "OPN2101A.bdix",
                                      "OPN2101A.bmix",
                                      "OPN2101A.pdf",
                                      "FrameSOC.blix"]
    assert get_instrument_files(mock_sftp, "") == ["OPN2101A.bdbx",
                                                   "OPN2101A.bdix",
                                                   "OPN2101A.bmix",
                                                   "FrameSOC.blix"]


def test_check_instrument_database_file_exists_returns_false_if_file_list_is_empty():
    file_list = []
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is False


def test_check_instrument_database_file_exists_returns_false_if_no_instrument_database_file_found():
    file_list = ["OPN2101A.bdix",
                 "OPN2101A.bmix",
                 "FrameSOC.blix"]
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is False


def test_check_instrument_database_file_exists_returns_false_if_different_database_file_found():
    file_list = ["LMS2101A.bdbx",
                 "LMS2101A.bdix",
                 "LMS2101A.bmix",
                 "FrameSOC.blix"]
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is False


def test_check_instrument_database_file_exists_returns_true_if_correct_instrument_database_file_found():
    file_list = ["oPn2101A.bDbX",
                 "OPN2101A.bdix",
                 "OPN2101A.bmix",
                 "FrameSOC.blix"]
    instrument_name = "OPN2101A"
    assert check_instrument_database_file_exists(file_list, instrument_name) is True


@patch.object(GoogleStorage, "get_blob", return_value=None)
def test_check_if_matching_file_in_bucket_returns_false_if_no_files(mock_get_blob):
    assert check_if_matching_file_in_bucket("OPN2101A", "OPN2101A") is False


@patch.object(GoogleStorage, "get_blob")
@patch.object(hashlib, "md5")
@patch("builtins.open")
def test_check_if_matching_file_in_bucket_returns_true_if_files_match(mock_open,
                                                                      mock_hashlib,
                                                                      mock_get_blob):
    mock_md5 = mock.MagicMock()
    mock_md5.digest.return_value = "123456789"
    mock_hashlib.return_value = mock_md5
    mock_get_blob.return_value = mock.MagicMock(md5_hash=pybase64.b64encode(b"123456789"), name="OPN2101A")
    assert check_if_matching_file_in_bucket("OPN2101A", "OPN2101A") is True


@patch.object(GoogleStorage, "get_blob")
@patch.object(hashlib, "md5")
@patch("builtins.open")
def test_check_if_matching_file_in_bucket_returns_false_hash_is_different(mock_open,
                                                                      mock_hashlib,
                                                                      mock_get_blob):
    mock_md5 = mock.MagicMock()
    mock_md5.digest.return_value = "ONS"
    mock_hashlib.return_value = mock_md5
    mock_get_blob.return_value = mock.MagicMock(md5_hash=pybase64.b64encode(b"123456789"), name="OPN2101A")
    assert check_if_matching_file_in_bucket("OPN2101A", "OPN2101A") is False


@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
def test_process_instrument_if_no_instrument_files(mock_upload_instrument,
                                                   mock_check_if_matching_file_in_bucket,
                                                   mock_get_instrument_files,
                                                   mock_delete_local_instrument_files,
                                                   mock_sftp):
    mock_get_instrument_files.return_value = []
    assert process_instrument(mock_sftp,
                              "ONS/OPN/OPN2101A/") == "No instrument files found in folder - ONS/OPN/OPN2101A/"
    mock_delete_local_instrument_files.assert_called_once()
    mock_check_if_matching_file_in_bucket.assert_not_called()
    mock_upload_instrument.assert_not_called()


@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
def test_process_instrument_if_no_instrument_database_file(mock_upload_instrument,
                                                           mock_check_if_matching_file_in_bucket,
                                                           mock_get_instrument_files,
                                                           mock_delete_local_instrument_files,
                                                           mock_sftp):
    mock_get_instrument_files.return_value = ["OPN2101A.bdix",
                                              "OPN2101A.bmix",
                                              "FrameSOC.blix",
                                              "foobar.bdbx"]
    assert process_instrument(mock_sftp, "ONS/OPN/OPN2101A/") == "Instrument database file not found - OPN2101A.bdbx"
    mock_delete_local_instrument_files.assert_called_once()
    mock_check_if_matching_file_in_bucket.assert_not_called()
    mock_upload_instrument.assert_not_called()
