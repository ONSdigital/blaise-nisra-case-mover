import logging
import os

from dataclasses import dataclass


@dataclass
class BucketConfig:
    bucket_name:  str

    @classmethod
    def from_env(cls):
        return cls(
            bucket_name=os.getenv("NISRA_BUCKET_NAME", "env_var_not_set")
        )

    def log(self):
        logging.info(f"bucket_name - {self.bucket_name}")
