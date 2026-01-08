"""Declares some useful package_level metadata"""

import importlib.metadata
from pathlib import Path

from platformdirs import site_data_dir

__version__ = importlib.metadata.version(__package__)

APP_NAME = __package__
ORGANIZATION = "AllenInstitute"

# On windows, DATA_DIR resolves to C:\ProgramData\{ORGANIZATION}\{APP_NAME}
DATA_DIR = Path(
    site_data_dir(
        APP_NAME,
        appauthor=ORGANIZATION,
        ensure_exists=True,
    )
)
