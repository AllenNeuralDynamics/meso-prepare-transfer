"""Logging configuration"""

import logging
import logging.handlers
from math import log
import sys
import os
from typing import Optional

from aind_mesoscope_user_schema_ui.utils.source_config import AppInfo


class LogServerHandler(logging.handlers.SocketHandler):
    """This handler attaches metadata to log messages such that logs can be ingested and parsed correctly by the onsite log server.
    These extra fields (rig id, comp id, project name, version) help users and system engineers filter and diagnose problems
    """

    def __init__(
        self,
        app_info: AppInfo,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.app_info = app_info
        self.formatter = logging.Formatter(
            datefmt="%Y-%m-%d %H:%M:%S",
            fmt="%(asctime)s\n%(name)s\n%(levelname)s\n%(funcName)s (%(filename)s:%(lineno)d)\n%(message)s",
        )

    def emit(self, record: logging.LogRecord) -> None:
        # Add extra attributes to the record
        record.project = self.app_info.name
        record.version = self.app_info.version
        record.rig_id = self.app_info.rig_id
        record.comp_id = self.app_info.comp_id
        record.extra = None  # set extra to None because this sends a pickled record
        super().emit(record)


def setup_logging(
    app_info: AppInfo,
    logserver_url: Optional[str] = None,
    log_level=logging.INFO,
):
    """Create log handler

    Parameters
    ----------
    log_file : filepath to send logging, optional
        by default None
    log_level : configure logging level, optional
        by default logging.INFO
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a formatter and set the format for logs
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create a console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # If log_file is provided, add a file handler
    file_handler = logging.FileHandler(app_info.log_file_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Set up log server handler
    if logserver_url:
        logger.addHandler(
            LogServerHandler(
                app_info,
                host=logserver_url.split(":")[0],
                port=int(logserver_url.split(":")[1]),
            )
        )

    # Define a global exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error(
            "Uncaught exception occurred", exc_info=(exc_type, exc_value, exc_traceback)
        )

    # Set the global exception handler
    sys.excepthook = handle_exception
