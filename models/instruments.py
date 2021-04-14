import datetime
import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Instrument:
    sftp_path: str
    bdbx_updated_at: Optional[datetime.datetime] = None
    bdbx_md5: Optional[str] = None
    files: List[str] = field(default_factory=list)

    def bdbx_file(self) -> Optional[str]:
        for file in self.files:
            if pathlib.Path(file).suffix.lower() == ".bdbx":
                return f"{self.sftp_path}/{file}"
        return None

    def get_blob_filepaths(self) -> Dict[str, str]:
        filepaths = {}
        folder_name = self.gcp_folder()
        for file in self.files:
            filepaths[file] = f"{folder_name}/{file.lower()}"
        return filepaths

    def get_bdbx_blob_filepath(self) -> Optional[str]:
        bdbx_file = self.bdbx_file()
        if not bdbx_file:
            return None
        bdbx_file = pathlib.PurePath(bdbx_file).name
        filepaths = self.get_blob_filepaths()
        if bdbx_file not in filepaths:
            return None
        return filepaths[bdbx_file]

    def gcp_folder(self) -> str:
        return pathlib.PurePath(self.sftp_path).name.lower()
