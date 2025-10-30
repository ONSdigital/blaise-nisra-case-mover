from google.auth.transport.requests import AuthorizedSession
from google.resumable_media import common, requests

from pkg.google_storage import GoogleStorage

# This has been taken from the blog post:
# https://dev.to/sethmlarson/python-data-streaming-to-google-cloud-storage-with-resumable-uploads-458h  # noqa: E501
# the idea is that by utilising resumable uploads we can stream data into a GCP file,
# rather than having to hold the entire file in memory/ on disk
# Usage:
#
# client = storage.Client()

# with GCSObjectStreamUpload(google_storage=google_storage, blob='blob') as s:
#     for _ in range(1024):
#         s.write(b'x' * 1024)


class GCSObjectStreamUpload(object):
    def __init__(
        self,
        google_storage: GoogleStorage,
        blob_name: str,
        chunk_size: int = 256 * 1024,
    ):
        self._bucket = google_storage.bucket
        self._blob = self._bucket.blob(blob_name)

        self._buffer = b""
        self._buffer_size = 0
        self._chunk_size = chunk_size
        self._read = 0

        self._transport = AuthorizedSession(
            credentials=google_storage.storage_client._credentials
        )
        self._request = None  # type: ignore # type: requests.ResumableUpload

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self.stop()

    def start(self):
        url = (
            f"https://www.googleapis.com/upload/storage/v1/b/"
            f"{self._bucket.name}/o?uploadType=resumable"
        )
        self._request = requests.ResumableUpload(
            upload_url=url, chunk_size=self._chunk_size
        )
        self._request.initiate(
            transport=self._transport,
            content_type="application/octet-stream",
            stream=self,
            stream_final=False,
            metadata={"name": self._blob.name},
        )

    def stop(self):
        if self._request:
            self._request.transmit_next_chunk(self._transport)

    def write(self, data: bytes) -> int:
        data_len = len(data)
        self._buffer_size += data_len
        self._buffer += data
        del data
        while self._buffer_size >= self._chunk_size:
            try:
                self._request and self._request.transmit_next_chunk(self._transport)
            except common.InvalidResponse:
                self._request and self._request.recover(self._transport)
        return data_len

    def read(self, chunk_size: int) -> bytes:
        # I'm not good with efficient no-copy buffering so if this is
        # wrong or there's a better way to do this let me know! :-)
        to_read = min(chunk_size, self._buffer_size)
        memview = memoryview(self._buffer)
        self._buffer = memview[to_read:].tobytes()
        self._read += to_read
        self._buffer_size -= to_read
        return memview[:to_read].tobytes()

    def tell(self) -> int:
        return self._read
