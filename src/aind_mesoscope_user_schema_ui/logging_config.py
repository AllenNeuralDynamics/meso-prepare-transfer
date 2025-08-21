"""Logging configuration"""

import logging
import logging.handlers
import sys
import os
from typing import Optional


class LogServerHandler(logging.handlers.SocketHandler):
    """This handler attaches metadata to log messages such that logs can be ingested and parsed correctly by the onsite log server.
    These extra fields (rig id, comp id, project name, version) help users and system engineers filter and diagnose problems
    """

    def __init__(
        self,
        project_name,
        version,
        rig_id=os.getenv("aibs_rig_id", "unknown"),
        comp_id=os.getenv("aibs_comp_id", "unknown"),
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.project_name = project_name
        self.rig_id = rig_id
        self.comp_id = comp_id
        self.version = version
        self.formatter = logging.Formatter(
            datefmt="%Y-%m-%d %H:%M:%S",
            fmt="%(asctime)s\n%(name)s\n%(levelname)s\n%(funcName)s (%(filename)s:%(lineno)d)\n%(message)s",
        )

    def emit(self, record: logging.LogRecord) -> None:
        # Add extra attributes to the record
        record.project = self.project_name
        record.rig_id = self.rig_id
        record.comp_id = self.comp_id
        record.version = self.version
        record.extra = None  # set extra to None because this sends a pickled record
        super().emit(record)


def setup_logging(
    app_name: str,
    app_version: str,
    log_file: Optional[str] = None,
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
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set up log server handler
    logger.addHandler(
        LogServerHandler(
            host=logserver_url.split(":")[0],
            port=int(logserver_url.split(":")[1]),
            project_name=app_name,
            version=app_version,
        )
    )

    # Define a global exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error(
            "Uncaught exception occurred", exc_info=(exc_type, exc_value, exc_traceback)
        )

    # Set the global exception handler
    sys.excepthook = handle_exception
