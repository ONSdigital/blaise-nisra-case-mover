import pytest
from unittest import mock
from unittest.mock import patch
from blaise_nisra_case_mover import *

@pytest.fixture
def mock_sftp():
    return mock.MagicMock()


def test_get_instrument_folders(mock_sftp):
    mock_sftp.listdir.return_value = ["OPN2101A",
                                      "OPN2004A",
                                      "foobar"]
    assert get_instrument_folders(mock_sftp, "") == ["OPN2101A",
                                                     "OPN2004A"]

def test_get_instrument_file(mock_sftp):
    mock_sftp.listdir.return_value = ["OPN2101A.blix",
                  "OPN2101A.bdbx",
                  "OPN2101A.bdix",
                  "OPN2101A.bmix",
                  "OPN2101A.pdf",
                  "framesock.blix"]
    assert get_instrument_files(mock_sftp, "") == ["OPN2101A.blix",
                                                   "OPN2101A.bdbx",
                                                   "OPN2101A.bdix",
                                                   "OPN2101A.bmix",
                                                   "framesock.blix"]


@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
def test_process_instrument_no_instrument_files(mock_upload_instrument,
                            mock_check_if_matching_file_in_bucket,
                            mock_get_instrument_files,
                            mock_delete_local_instrument_files,
                            mock_sftp):
    mock_get_instrument_files.return_value = []
    assert process_instrument(mock_sftp, "OPN2101A") == "No instrument files found in folder: OPN2101A"
    mock_upload_instrument.assert_not_called()
    mock_delete_local_instrument_files.assert_called_once()

@patch("blaise_nisra_case_mover.delete_local_instrument_files")
@patch("blaise_nisra_case_mover.get_instrument_files")
@patch("blaise_nisra_case_mover.check_if_matching_file_in_bucket")
@patch("blaise_nisra_case_mover.upload_instrument")
def test_process_instrument_no_bdbx_file(mock_upload_instrument,
                            mock_check_if_matching_file_in_bucket,
                            mock_get_instrument_files,
                            mock_delete_local_instrument_files,
                            mock_sftp):
    mock_get_instrument_files.return_value = ["OPN2101A.blix",
                                                   "OPN2101A.bdix",
                                                   "OPN2101A.bmix",
                                                   "framesock.blix"]
    response = process_instrument(mock_sftp, "OPN2101A.bdbx")
    mock_upload_instrument.assert_not_called()
    mock_delete_local_instrument_files.assert_called_once()
    assert response == "No bdbx found"

def test_check_instrument_database_file_exists_returns_false_if_list_is_empty():
    file_list = []
    instrument_name = "OPN2101A"
    response = check_instrument_database_file_exists(file_list, instrument_name)
    assert response == False


def test_check_instrument_database_file_exists_returns_false_if_no_instrument_database_found():
    file_list = ["foobar.bdix", "framework.bdbx"]
    instrument_name = "OPN2101A"
    response = check_instrument_database_file_exists(file_list, instrument_name)
    assert response == False


def test_check_instrument_database_file_exists_returns_true_if_instrument_database_found():
    file_list = ["OPN2101A.bdbx"]
    instrument_name = "OPN2101A"
    response = check_instrument_database_file_exists(file_list, instrument_name)
    assert response == True


def test_check_instrument_database_file_exists_returns_false_if_different_database_found():
    file_list = ["OPN2004A.bdbx"]
    instrument_name = "OPN2104A"
    response = check_instrument_database_file_exists(file_list, instrument_name)
    assert response == False
