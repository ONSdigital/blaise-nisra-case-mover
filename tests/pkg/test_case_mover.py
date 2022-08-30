import io
import logging
from datetime import datetime
from unittest import mock

import pytest
import requests

from models import Instrument
from pkg.case_mover import CaseMover
from pkg.gcs_stream_upload import GCSObjectStreamUpload
from pkg.google_storage import GoogleStorage


@mock.patch.object(GoogleStorage, "get_blob_md5")
def test_bdbx_md5_changed_when_match(
    mock_get_blob_md5, google_storage, config, mock_sftp
):
    mock_get_blob_md5.return_value = "my_lovely_md5"
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "oPn2103A.BdBx",
        ],
    )
    case_mover = CaseMover(google_storage, config, mock_sftp)
    assert case_mover.bdbx_md5_changed(instrument) is False
    mock_get_blob_md5.assert_called_with("opn2103a/opn2103a.bdbx")


@mock.patch.object(GoogleStorage, "get_blob_md5")
def test_bdbx_md5_changed_when_not_match(
    mock_get_blob_md5, google_storage, config, mock_sftp
):
    mock_get_blob_md5.return_value = "another_md5_which_is_less_lovely"
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "oPn2103A.BdBx",
        ],
    )
    case_mover = CaseMover(google_storage, config, mock_sftp)
    assert case_mover.bdbx_md5_changed(instrument) is True
    mock_get_blob_md5.assert_called_with("opn2103a/opn2103a.bdbx")


@mock.patch.object(GoogleStorage, "get_blob_md5")
def test_bdbx_md5_changed_when_no_gcp_file(
    mock_get_blob_md5, google_storage, config, mock_sftp
):
    mock_get_blob_md5.return_value = None
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "oPn2103A.BdBx",
        ],
    )
    case_mover = CaseMover(google_storage, config, mock_sftp)
    assert case_mover.bdbx_md5_changed(instrument) is True
    mock_get_blob_md5.assert_called_with("opn2103a/opn2103a.bdbx")


@mock.patch.object(CaseMover, "sync_file")
def test_sync_instrument(mock_sync_file, google_storage, config, mock_sftp):
    instrument = Instrument(
        sftp_path="./ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "oPn2103A.BdBx",
        ],
    )
    case_mover = CaseMover(google_storage, config, mock_sftp)
    case_mover.sync_instrument(instrument)
    mock_sync_file.assert_called_once_with(
        "opn2103a/opn2103a.bdbx", "./ONS/OPN/OPN2103A/oPn2103A.BdBx"
    )


@mock.patch.object(GCSObjectStreamUpload, "write")
@mock.patch.object(GCSObjectStreamUpload, "stop")
@mock.patch.object(GCSObjectStreamUpload, "start")
@mock.patch.object(GCSObjectStreamUpload, "__init__")
def test_sync_file(
    mock_stream_upload_init,
    _mock_stream_upload_start,
    _mock_stream_upload_stop,
    mock_stream_upload,
    google_storage,
    config,
    mock_sftp,
    mock_sftp_connection,
    mock_stat,
    fake_sftp_file,
):
    fake_content = b"foobar this is a fake file"
    config.bufsize = 1
    mock_stream_upload_init.return_value = None
    mock_sftp_connection.stat.return_value = mock_stat(st_size=len(fake_content))

    fake_file = fake_sftp_file(fake_content)
    fake_gcp_file = io.BytesIO(b"")
    mock_stream_upload.side_effect = lambda bytes: fake_gcp_file.write(bytes)
    mock_sftp_connection.open.return_value = fake_file
    case_mover = CaseMover(google_storage, config, mock_sftp)
    case_mover.sync_file("opn2103a/opn2103a.bdbx", "./ONS/OPN/OPN2103A/oPn2103A.BdBx")
    assert fake_file.read() == fake_gcp_file.read()
    assert mock_stream_upload.call_count == len(fake_content)


@mock.patch.object(GCSObjectStreamUpload, "write")
@mock.patch.object(GCSObjectStreamUpload, "stop")
@mock.patch.object(GCSObjectStreamUpload, "start")
@mock.patch.object(GCSObjectStreamUpload, "__init__")
def test_sync_file_exception(
    mock_stream_upload_init,
    _mock_stream_upload_start,
    _mock_stream_upload_stop,
    mock_stream_upload,
    google_storage,
    config,
    mock_sftp,
    mock_sftp_connection,
    mock_stat,
    fake_sftp_file,
    caplog,
):
    config.bufsize = 1
    mock_stream_upload_init.return_value = None
    mock_sftp_connection.stat.side_effect = Exception("I exploded the thing")

    with caplog.at_level(logging.ERROR):
        case_mover = CaseMover(google_storage, config, mock_sftp)
        case_mover.sync_file(
            "opn2103a/opn2103a.bdbx", "./ONS/OPN/OPN2103A/oPn2103A.BdBx"
        )

    log_records = [(record.levelname, record.message) for record in caplog.records]
    assert (
        "ERROR",
        "Fatal error while syncing file ./ONS/OPN/OPN2103A/oPn2103A.BdBx to opn2103a/opn2103a.bdbx",
    ) in log_records
    assert "I exploded the thing" in caplog.text


@mock.patch.object(requests, "post")
def test_send_request_to_api(mock_requests_post, google_storage, config, mock_sftp):
    case_mover = CaseMover(google_storage, config, mock_sftp)
    case_mover.send_request_to_api("opn2101a")
    mock_requests_post.assert_called_once_with(
        (
            f"http://{config.blaise_api_url}/api/v2/serverparks/"
            + f"{config.server_park}/questionnaires/opn2101a/data"
        ),
        json={"questionnaireDataPath": "opn2101a"},
        headers={"content-type": "application/json"},
        timeout=1,
    )


def test_instrument_exists_in_blaise(google_storage, config, mock_sftp, requests_mock):
    requests_mock.get(
        f"http://{config.blaise_api_url}/api/v2/serverparks/"
        + f"{config.server_park}/questionnaires/opn2101a/exists",
        text="false",
    )
    case_mover = CaseMover(google_storage, config, mock_sftp)
    assert case_mover.instrument_exists_in_blaise("opn2101a") is False


def test_instrument_exists_in_blaise_exists(
    google_storage, config, mock_sftp, requests_mock
):
    requests_mock.get(
        f"http://{config.blaise_api_url}/api/v2/serverparks/"
        + f"{config.server_park}/questionnaires/opn2101a/exists",
        text="true",
    )
    case_mover = CaseMover(google_storage, config, mock_sftp)
    assert case_mover.instrument_exists_in_blaise("opn2101a") is True


@mock.patch.object(CaseMover, "instrument_exists_in_blaise")
def test_filter_existing_instruments(
    mock_instrument_exists_in_blaise, google_storage, config, mock_sftp
):
    mock_instrument_exists_in_blaise.side_effect = (
        lambda instrument_name: True if instrument_name.startswith("opn") else False
    )
    instruments = {
        "OPN2101A": Instrument(sftp_path="./ONS/OPN/OPN2101A"),
        "LMS2101A": Instrument(sftp_path="./ONS/OPN/LMS2101A"),
        "lMS2101A": Instrument(sftp_path="./ONS/OPN/lMS2101A"),
        "lMS2101a": Instrument(sftp_path="./ONS/OPN/lMS2101a"),
    }
    case_mover = CaseMover(google_storage, config, mock_sftp)
    filtered_instruments = case_mover.filter_existing_instruments(instruments)
    assert filtered_instruments == {
        "OPN2101A": Instrument(sftp_path="./ONS/OPN/OPN2101A"),
    }


@mock.patch.object(GoogleStorage, "list_blobs")
def test_get_instrument_blobs(
    mock_list_blobs, google_storage, config, mock_sftp, fake_blob
):
    case_mover = CaseMover(google_storage, config, mock_sftp)
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "oPn2103A.BdBx",
        ],
    )
    mock_list_blobs.return_value = [
        fake_blob("foobar"),
        fake_blob("opn2103a.bdbx"),
        fake_blob("opn2101a/oPn2101A.BdIx"),
        fake_blob("opn2103a/oPn2103A.BdIx"),
        fake_blob("opn2103a/FrameSOC.blix"),
    ]
    assert case_mover.get_instrument_blobs(instrument) == [
        "opn2103a.bdix",
        "framesoc.blix",
    ]


@mock.patch.object(CaseMover, "get_instrument_blobs")
def test_gcp_missing_files_none(
    mock_get_instrument_blobs, google_storage, config, mock_sftp, fake_blob
):
    case_mover = CaseMover(google_storage, config, mock_sftp)
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "oPn2103A.BdBx",
            "opn2103a.bdix",
            "framesoc.blix",
        ],
    )
    mock_get_instrument_blobs.return_value = [
        "opn2103a.bdix",
        "framesoc.blix",
        "opn2103a.bdbx",
    ]

    assert case_mover.gcp_missing_files(instrument) is False


@mock.patch.object(CaseMover, "get_instrument_blobs")
def test_gcp_missing_files_missing(
    mock_get_instrument_blobs, google_storage, config, mock_sftp, fake_blob
):
    case_mover = CaseMover(google_storage, config, mock_sftp)
    instrument = Instrument(
        sftp_path="ONS/OPN/OPN2103A",
        bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
        bdbx_md5="my_lovely_md5",
        files=[
            "oPn2103A.BdBx",
            "opn2103a.bdix",
        ],
    )
    mock_get_instrument_blobs.return_value = [
        "opn2103a.bdix",
        "framesoc.blix",
    ]

    assert case_mover.gcp_missing_files(instrument) is True


@pytest.mark.parametrize(
    "bdbx_changed,gcp_missing_files,result",
    [
        (True, True, True),
        (True, False, True),
        (False, True, True),
        (False, False, False),
    ],
)
def test_instrument_needs_updating(
    google_storage, config, mock_sftp, bdbx_changed, gcp_missing_files, result
):
    with mock.patch.object(CaseMover, "bdbx_md5_changed", return_value=bdbx_changed):
        with mock.patch.object(
            CaseMover, "gcp_missing_files", return_value=gcp_missing_files
        ):
            case_mover = CaseMover(google_storage, config, mock_sftp)
            instrument = Instrument(
                sftp_path="ONS/OPN/OPN2103A",
                bdbx_updated_at=datetime.fromisoformat("2021-05-20T10:21:53+00:00"),
                bdbx_md5="my_lovely_md5",
                files=[
                    "oPn2103A.BdBx",
                ],
            )
            assert case_mover.instrument_needs_updating(instrument) is result
