import io
from datetime import datetime
from unittest import mock

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
    assert case_mover.bdbx_md5_changed(instrument) is True
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
    assert case_mover.bdbx_md5_changed(instrument) is False
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
    assert case_mover.bdbx_md5_changed(instrument) is False
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


@mock.patch.object(requests, "post")
def test_send_request_to_api(mock_requests_post, google_storage, config, mock_sftp):
    case_mover = CaseMover(google_storage, config, mock_sftp)
    case_mover.send_request_to_api("opn2101a")
    mock_requests_post.assert_called_once_with(
        (
            f"http://{config.blaise_api_url}/api/v1/serverparks/"
            + f"{config.server_park}/instruments/opn2101a/data"
        ),
        json={"instrumentDataPath": "opn2101a"},
        headers={"content-type": "application/json"},
        timeout=10,
    )
