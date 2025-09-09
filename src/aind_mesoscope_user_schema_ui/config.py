from typing import Optional
from pathlib import Path

from aind_mesoscope_user_schema_ui.utils.source_config import SuperConfig, AppInfo
from aind_mesoscope_user_schema_ui import __version__

app_info = AppInfo(name="meso_prepare_transfer", version=__version__)


class Config(SuperConfig, app_info=app_info):

    logserver_url: str = "eng-logtools.corp.alleninstitute.org:9000"

    acquisition_dir: str = "D:/scanimage_ophys/data"
    behavior_dir: str  # = "//W10SV109650002/mvr/data"

    # transfer_endpoint: str = "http://aind-data-transfer-service/api/v2/submit_jobs"
    transfer_endpoint: str | None = None
    transfer_service_job_type: str = "multi_pophys_suite2p_cellpose"

    platform: str = "multiplane_ophys"
    manifest_directory: str = (
        "C:/Users/svc_mesoscope/Documents/aind_watchdog_service/manifest"
    )
    s3_bucket: str = "open"
    capsule_id: str = "e3ac6a41-c578-4798-b251-3b316674dce2"
    mount: str = "ophys_mount"
    destination: str = "//allen/aind/scratch/2p-working-group/data-uploads"
    schemas: list[str] = [
        "C:/ProgramData/aind/rig.json",
        "session.json",
        "data_description.json",
    ]
    # schedule_time: Optional[str] = 'now"'
    force_cloud_sync: bool = True

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
            "*timeseries.roi",
            "*timeseries.tiff",
            "*vasculature.tif",
            "*_timeseries_Motion*.csv",
            "*_timeseries_Motion_Corrected*.csv",
            "parent_session_depth_images/*_depth.tif",
            "parent_session_surface_images/*_surface.tif",
            "sorted_local_z_stacks/*.tif",
        ],
        "behavior-videos": [
            -"*Behavior*.mp4"
            - "*Face*.mp4"
            - "*Eye*.mp4"
            - "*Behavior*.json"
            - "*Face*.json"
            - "*Eye*.json"
            - "*Nose*.mp4"
            - "*Nose*.json"
        ],
        "behavior": [
            "*stim.pkl",
            "*stim_table.csv",
            "*sync.h5",
        ],
    }


if __name__ == "__main__":
    cfg = Config()
    print(cfg.model_dump_json(indent=2))
