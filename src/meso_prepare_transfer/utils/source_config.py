"""Utilities and pattern for configuration management.

Loads/saves configuration to a server with get/post endpoints

Usage example:
```python

# Specify application config in a model
class MyConfig(
    BaseSettings,
    validate_default=True,
    extra="ignore",
    cli_parse_args=True,
    cli_ignore_unknown_args=True,
):

    param1: str
    param2: int = 42
    param3: float = 3.14


# Fetch and load config explicitly
def main():
    config_file = fetch_config_from_server(
        config_server_url="http://eng-tools:8888/api/v1beta/configs/projects/",
        app_name="example_app",
        rig_name=os.getenv("aibs_comp_id", "unknown"),
        cache_file=app_data_dir("example_app") / "config" / "config_server_response.json",
    )
    config_data = json.loads(config_file.read_text())
    # instantiate config object
    config = MyConfig(**config_data)  # loads from env vars, cli args
    print(config)

```

Depends on [
    'requests',
    'pydantic-settings',
    'platformdirs',
]
"""

import datetime
import json
from pathlib import Path
from typing import TypeVar
import shutil
import warnings
import logging

import requests
from pydantic_settings import BaseSettings


##### Utilities


# def app_data_dir(app_name: str, organization: str = "AllenInstitute") -> Path:
#     """Get or create a data directory for the application"""
#     return Path(
#         site_data_dir(
#             app_name,
#             appauthor=organization,
#             ensure_exists=True,
#         )
#     )


def fetch_config_from_server(
    config_server_url: str,
    app_name: str,
    rig_name: str,
    cache_file: Path,  # this could maybe have a default option
) -> Path:
    """Uses http GET to fetch config from server, caches locally"""

    url = config_server_url + app_name

    response = requests.get(url, params={"rig_name": rig_name})

    if response.status_code == 200:
        logging.info(f"Fetched config from {config_server_url} for rig {rig_name}")
        cache_data(response.text, cache_file)
    else:
        warnings.warn(
            f"Failed to fetch config from {config_server_url} for rig {rig_name}. "
            f"Status code: {response.status_code}, Response: {response.text} "
            f"Using cached config if available: {cache_file}"
        )

    return cache_file


def cache_data(data: str, cache_file: Path):
    """Cache the returned config data"""
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    if cache_file.exists():
        if data == cache_file.read_text():
            return

        # Backup previous config with timestamp
        timestamp = datetime.datetime.strftime(datetime.datetime.now(), "%y%m%d-%H%M%S")
        backup_file = f"{cache_file}.{timestamp}.bck"
        # logging.info(f"Copying previous configuration to {backup_file}")
        shutil.copyfile(cache_file, backup_file)

    # Write new info into cache file
    cache_file.write_text(data)


def write_config_to_server(
    config_server_url: str,
    app_name: str,
    rig_name: str,
    data: dict,
):
    """Write config to server"""
    url = config_server_url + app_name

    response = requests.post(url, json={"rig_name": rig_name, "config": data})

    if response.status_code == 200:
        logging.info(f"Wrote config to {config_server_url} for rig {rig_name}")
    else:
        warnings.warn(
            f"Failed to write config to {config_server_url} for rig {rig_name}. "
            f"Status code: {response.status_code}, Response: {response.text} "
        )


##### Util to fetch/cache/instantiate config object

T = TypeVar("Config", bound=BaseSettings)


def get_config(config_class: type[T], config_server_url: str, app_name: str, rig_name: str, cache_file: Path) -> T:
    """Fetch config from server and return as an instance of config_class"""
    config_file = fetch_config_from_server(
        config_server_url=config_server_url,
        app_name=app_name,
        rig_name=rig_name,
        cache_file=cache_file,
    )
    config_data = json.loads(config_file.read_text())
    return config_class(**config_data)


#### Fancy Pydantic Settings Source version

# # This caches returned configs as json, but maybe should use yaml?
# # Using json somewhat implies that this is a return from a web API and shouldn't be edited
# class HttpConfigSettingsSource(JsonConfigSettingsSource):
#     """
#     A source class that loads configuration from an http endpoint, caching returns locally
#     """

#     def __init__(
#         self,
#         settings_cls: type[BaseSettings],
#         cache_file_name: str = "config_server_response.json",
#     ):
#         config_file = fetch_config_from_server(
#             config_server_url=config_server_url,
#             app_name=app_name,
#             rig_name=rig_name,
#             cache_file=cache_file,
#         )
#         super().__init__(settings_cls, config_file)


# class SuperConfig(
#     BaseSettings,
#     validate_default=True,
#     extra="ignore",
#     cli_parse_args=True,
#     cli_ignore_unknown_args=True,
# ):
#     # Specify source loading order (yaml file, env vars, etc)
#     @classmethod
#     def settings_customise_sources(
#         cls,
#         settings_cls: type[BaseSettings],
#         init_settings: PydanticBaseSettingsSource,
#         env_settings: PydanticBaseSettingsSource,
#         dotenv_settings: PydanticBaseSettingsSource,
#         file_secret_settings: PydanticBaseSettingsSource,
#     ) -> tuple[PydanticBaseSettingsSource, ...]:
#         """Specify order of settings sources (yaml file, env vars, etc)"""
#         return (
#             init_settings,
#             env_settings,
#             dotenv_settings,
#             file_secret_settings,
#             #### No need to load from local yaml if loading from server
#             # YamlConfigSettingsSource(settings_cls, yaml_file=app_info.config_file_path),
#             HttpConfigSettingsSource(settings_cls),
#         )


# def main():
#     config_file = fetch_config_from_server(
#         config_server_url=os.getenv("ALLENINST_CONFIG_API_URL", "http://eng-tools:8888/api/v1beta/configs/projects/"),
#         app_name="my_camera_driver",
#         rig_name=os.getenv("aibs_comp_id", "unknown"),
#         cache_file=app_data_dir("my_camera_driver") / "config" / "config_server_response.json",
#     )
#     config_data = json.loads(config_file.read_text())

#     # instantiate config object
#     config = MyConfig(**config_data) # will also pull from cli args
#     print(config)
