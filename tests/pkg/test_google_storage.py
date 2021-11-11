from unittest import mock

import pybase64

from pkg.google_storage import GoogleStorage


def test_get_blob_md5_no_blob():
    google_storage = GoogleStorage("test")
    google_storage.bucket = mock.MagicMock()
    google_storage.bucket.get_blob.return_value = None
    assert google_storage.get_blob_md5("test.txt") is None


def test_get_blob_md5():
    mock_md5 = mock.MagicMock()
    mock_md5.md5_hash = pybase64.b64encode(b"foobar")
    google_storage = GoogleStorage("test")
    google_storage.bucket = mock.MagicMock()
    google_storage.bucket.get_blob.return_value = mock_md5
    assert google_storage.get_blob_md5("test.txt") == "666f6f626172"
