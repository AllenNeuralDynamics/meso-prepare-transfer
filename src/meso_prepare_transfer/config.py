"""App configuration"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Config(
    BaseSettings,
    validate_default=True,
    extra="ignore",
    cli_parse_args=True,
    cli_ignore_unknown_args=True,
):
    """Configuration used by meso-prepare-transfer, with defaults"""

    logserver_url: str = "eng-logtools.corp.alleninstitute.org:9000"

    acquisition_dir: Path = "D:/scanimage_ophys/data"
    behavior_video_dir: Path = "//W10SV109650002/mvr/data"

    # session_endpoint: str = "http://lims2/ophys_sessions.json?id={}"

    manifest_directory: Path = "C:/Users/svc_mesoscope/Documents/aind_watchdog_service/manifest"
    schemas: list[str] = [
        "C:/ProgramData/aind/rig.json",
        "session.json",
        "data_description.json",
    ]

    watchdog_manifest_kwargs: dict = {
        "schedule_time": "03:00:00",
        "destination": "//allen/aind/scratch/2p-working-group/data-uploads",
        "platform": "multiplane-ophys",
        "transfer_service_job_type": "multi_pophys_suite2p_cellpose",
        "delete_modalities_source_after_success": False,
    }

    investigators: dict[str, list[str]] = {
        "Learning mFISH-V1omFISH": [
            "Marina Garrett",
            "Peter Groblewski",
            "Anton Arkhipov",
            "Omid Zobeiri",
        ],
        "OpenScope": ["Jerome Lecoq"],
    }

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
            "*Behavior*.mp4",
            "*Face*.mp4",
            "*Eye*.mp4",
            "*Behavior*.json",
            "*Face*.json",
            "*Eye*.json",
            "*Nose*.mp4",
            "*Nose*.json",
        ],
        "behavior": [
            "*stim.pkl",
            "*stim_table.csv",
            "*sync.h5",
        ],
    }
