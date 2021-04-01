import datetime
import pathlib
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Instrument:
    sftp_path: str
    bdbx_updated_at: datetime.datetime = None
    bdbx_md5: str = None
    files: List[str] = field(default_factory=list)

    def bdbx_file(self) -> Optional[str]:
        for file in self.files:
            if pathlib.Path(file).suffix.lower() == ".bdbx":
                return f"{self.sftp_path}/{file}"
        return None

    def get_blob_filepaths(self) -> str:
        filepaths = {}
        folder_name = self.gcp_folder()
        for file in self.files:
            extension = pathlib.Path(file).suffix.lower()
            filepaths[extension] = f"{folder_name}/{file.lower()}"
        return filepaths

    def gcp_folder(self) -> str:
        return pathlib.PurePath(self.sftp_path).name.lower()
