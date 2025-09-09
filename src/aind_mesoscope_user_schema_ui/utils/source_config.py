"""Utilities and pattern for configuration management.

Loads/saves configuration to a server with get/post endpoints

Usage example:
```python
# specify information about the application
app_info = AppInfo(name="my_camera_driver", version="0.1.0")

class CameraConfig(SuperConfig, app_info=app_info):

    # Specify app-specific settings and parameters
    camera_id: str
    exposure: float = 33.3
    gain: float = 1.0
    frame_rate: float = 30.0

class Camera:
    def __init__(self, config: CameraConfig):
        self.config = config
        self.set_gain(self.config.gain)
        ...

def main():
    # instantiate config object, which fetches config from server or cli args
    config = CameraConfig()
    camera = Camera(config)
```

Depends on [
    'requests',
    'pydantic-settings',
    'platformdirs',
]
"""

import datetime
from pathlib import Path
from typing import Optional
import os
import platform
import shutil
import warnings
import logging

from pydantic import computed_field, field_validator
import requests
from platformdirs import site_data_dir
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    JsonConfigSettingsSource,
)
from pydantic._internal._config import config_keys as pydantic_settings_subclass_keys


class AppInfo(BaseSettings):
    """Information about the application"""

    name: str
    version: str
    computer: str = platform.node()
    rig_id: str = os.getenv("aibs_rig_id", "unknown")
    comp_id: str = os.getenv("aibs_comp_id", "unknown")
    organization: str = "AllenInstitute"
    config_server_url: str = os.getenv(
        "ALLENINST_CONFIG_API_URL",
        "http://eng-tools:8888/api/v1beta/configs/projects/",
    )

    @field_validator("config_server_url", mode="after")
    def validate_config_server_url(cls, v: str) -> str:
        if not v.endswith("/"):
            return v + "/"
        return v

    @computed_field
    @property
    def data_dir(self) -> Path:
        """A directory in ProgramData"""
        return Path(
            site_data_dir(
                self.name,
                appauthor=self.organization,
                ensure_exists=True,
            )
        )

    @computed_field
    @property
    def config_file_path(self, file_type: str = "yml") -> Path:
        """Path to a file to load configuration from"""
        config_dir = self.data_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / f"{self.name}.{file_type}"

    @computed_field
    @property
    def log_file_path(self) -> Path:
        """Path to a file to load configuration from"""
        config_dir = self.data_dir / "logs"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / f"{self.name}.log"


# This caches returned configs as json, but maybe should use yaml?
# Using json somewhat implies that this is a return from a web API and shouldn't be edited
class HttpConfigSettingsSource(JsonConfigSettingsSource):
    """
    A source class that loads configuration from an http endpoint, caching returns locally
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        cache_file_name: str = "config_server_response.json",
    ):

        app_info: AppInfo = settings_cls.model_config.get("app_info")
        self.cache_file = app_info.config_file_path.parent / cache_file_name

        url = app_info.config_server_url + app_info.name

        response = requests.get(url, params={"rig_name": app_info.comp_id})

        if response.status_code == 200:
            logging.info(
                f"Fetched config from {app_info.config_server_url} for rig {app_info.comp_id}"
            )
            self.cache_return(response.text, app_info)

            super().__init__(settings_cls, self.cache_file)
        else:
            warnings.warn(
                f"Failed to fetch config from {app_info.config_server_url} for rig {app_info.comp_id}. "
                f"Status code: {response.status_code}, Response: {response.text} "
                f"Using cached config if available: {self.cache_file}"
            )
            super().__init__(settings_cls, self.cache_file)

            # TODO: we might want to save a failure flag file so the server failure is tracked
            # self.write_failure_flag_file()

    def cache_return(self, data: str, app_info: AppInfo):
        """Cache the returned config data"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        if self.cache_file.exists():
            if data == self.cache_file.read_text():
                return

            # TODO:
            if self.check_for_failure_flag_file():
                # Could be a merge conflict, select which one to use
                pass

            # Backup previous config with timestamp
            timestamp = datetime.datetime.strftime(
                datetime.datetime.now(), "%y%m%d-%H%M%S"
            )
            backup_file = f"{self.cache_file}.{timestamp}.bck"
            # logging.info(f"Copying previous configuration to {backup_file}")
            shutil.copyfile(self.cache_file, backup_file)

        # Write new info into cache file
        self.cache_file.write_text(data)


# Add key to set of recognized config keys for pydantic settings subclasses
# so that we can pass app_info to SuperConfig subclasses
pydantic_settings_subclass_keys.add("app_info")


class SuperConfig(
    BaseSettings,
    validate_default=True,
    extra="ignore",
    cli_parse_args=True,
    cli_ignore_unknown_args=True,
):

    # Specify source loading order (yaml file, env vars, etc)
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Specify order of settings sources (yaml file, env vars, etc)"""
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            #### No need to load from local yaml if loading from server
            # YamlConfigSettingsSource(settings_cls, yaml_file=app_info.config_file_path),
            HttpConfigSettingsSource(settings_cls),
        )

    # def save_config(self):  # TODO: Add this functionality to this object and server
    #     """try to write to server, failover to local file"""

    #     self.model_config.get("app_info")
    #     try:
    #         requests.post(url, data=self.model_dump_json())
    #     except Exception as e:
    #         logging.error(f"Failed to write config to server: {e}")
    #         # Write to local file as fallback
    #         local_file.write(self.model_dump_json())

    #         Maybe should save a failure flag file so the server failure is tracked
    #         and the new changes are not overwritten by a server fetch


### TODO: think about composability of configs
# should be fine, but might be edge cases, especially when it comes to load/write from server
# Might have to add a _is_top_level flag to forward write requests to top level object
