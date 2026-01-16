"""Entry point for meso-prepare-transfer tool"""

import os
import json

from cyclopts import App
from loguru import logger

from meso_prepare_transfer.business_logic import process_dataset

from .utils.source_config import fetch_config_from_server
from .utils.logging_config import setup_logger

from meso_prepare_transfer import __version__, APP_NAME, DATA_DIR
from meso_prepare_transfer.config import Config

app = App()


@app.default()
def main(username: str, session_id: str):
    """Fetch config, setup logging, process a single dataset"""
    logger.info("Fetching meso-prepare-transfer config from server")
    config_file = fetch_config_from_server(
        config_server_url=os.getenv("ALLENINST_CONFIG_API_URL", "http://eng-tools:8888/api/v1beta/configs/projects/"),
        app_name=APP_NAME,
        rig_name=os.getenv("aibs_comp_id", "unknown"),
        cache_file=DATA_DIR / "config" / "config_server_response.json",
    )
    config_data = json.loads(config_file.read_text())

    # instantiate config object
    config = Config(**config_data)  # will also pull from cli args

    setup_logger(
        APP_NAME,
        __version__,
        log_file=DATA_DIR / "logs" / f"{APP_NAME}.log",
        logserver_url=config.logserver_url,
    )

    with logger.contextualize(session_id=session_id, username=username):
        process_dataset(username, session_id, config)


if __name__ == "__main__":
    app()
