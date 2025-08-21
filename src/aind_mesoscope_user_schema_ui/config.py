from pathlib import Path

from platformdirs import site_data_dir
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

from aind_mesoscope_user_schema_ui import APP_NAME

app_data_dir = Path(
    site_data_dir(
        APP_NAME,
        appauthor="AllenInstitute",
        ensure_exists=True,
    )
)

config_file = app_data_dir / "config" / f"{APP_NAME}.yml"


class Config(
    BaseSettings,
    validate_default=True,
    extra="ignore",
    yaml_file=config_file,
    cli_parse_args=True,
    cli_ignore_unknown_args=True,
):
    logserver_url: str = "eng-logtools.corp.alleninstitute.org:9000"
    log_file: Path = app_data_dir / "logs" / f"{APP_NAME}.log"

    acquisition_dir: str = "D:/data"
    behavior_dir: str = "D:/behavior/data"

    platform: str = "multiplane_ophys"
    manifest_directory: str = "D:/aind-watchdog-service-manifest"
    s3_bucket: str = "scratch"
    capsule_id: str = "56bf687b-dbcd-4b93-a650-21b8584036ff"
    mount: str = "multiplane-ophys_726433_2024-05-14_08-13-02"
    destination: str = "//allen/aind/scratch/2p-working-group/data-uploads"
    schemas: list[str] = ["rig.json", "session.json"]

    # What files and modalities service is expected to move; glob patterns OK
    modalities: dict[str, list[str]] = {
        "pophys": [
            "*_averaged_depth.tiff",
            "*_averaged_surface.tiff",
            "*cortical_z_stack*.tiff",
            "*fullfield.roi",
            "*fullfield.tiff",
            "*local_z_stack*.tiff",
            "*platform.json",
            "*reticle.tif",
            "*surface.roi",
            "*sync.h5",
            "*timeseries.roi",
            "*timeseries.tiff",
            "*vasculature.tif",
        ],
        "behavior-videos": [
            "*Behavior*.mp4",
            "*Face*.mp4",
            "*Eye*.mp4",
            "*Behavior*.json",
            "*Face*.json",
            "*Eye*.json",
        ],
        "behavior": [
            "*stim.pkl",
            "*stim_table.csv",
        ],
    }

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
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls),
        )
