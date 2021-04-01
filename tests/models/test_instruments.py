from models.instruments import Instrument


def test_bdbx_file_no_bdbx():
    instrument = Instrument(sftp_path="", files=["foo.bdix"])
    assert instrument.bdbx_file() is None


def test_bdbx_file_with_bdbx():
    instrument = Instrument(
        sftp_path="path/to/file", files=["foo.bdix", "bar.bdbx", "fish.zip"]
    )
    assert instrument.bdbx_file() == "path/to/file/bar.bdbx"


def test_get_blob_filepaths():
    instrument = Instrument(
        sftp_path="path/to/OPN2101A", files=["foo.bdix", "OPn2101A.bDbX", "fish.zip"]
    )
    assert instrument.get_blob_filepaths() == {
        ".bdbx": "opn2101a/opn2101a.bdbx",
        ".bdix": "opn2101a/foo.bdix",
        ".zip": "opn2101a/fish.zip",
    }


def test_gcp_folder():
    instrument = Instrument(
        sftp_path="path/to/OPN2101A", files=["foo.bdix", "OPn2101A.bDbX", "fish.zip"]
    )
    assert instrument.gcp_folder() == "opn2101a"
