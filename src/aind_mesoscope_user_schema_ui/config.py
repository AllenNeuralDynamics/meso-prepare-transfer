from pathlib import Path

from aind_mesoscope_user_schema_ui.utils.source_config import SuperConfig, AppInfo
from aind_mesoscope_user_schema_ui import __version__

app_info = AppInfo(name="meso_prepare_transfer", version=__version__)


class Config(SuperConfig, app_info=app_info):

    logserver_url: str = "eng-logtools.corp.alleninstitute.org:9000"

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


if __name__ == "__main__":
    cfg = Config()
    print(cfg.model_dump_json(indent=2))
