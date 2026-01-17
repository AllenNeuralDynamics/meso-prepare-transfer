"""Functions to process a mesoscope dataset for transfer off-rig"""

from datetime import datetime, timedelta

from pathlib import Path
import sys
import json

from loguru import logger

from aind_watchdog_service.models import ManifestConfig
from aind_data_schema.core.data_description import Funding, RawDataDescription
from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.platforms import Platform
from aind_metadata_mapper.mesoscope.models import JobSettings
from aind_metadata_mapper.mesoscope.session import MesoscopeEtl

from meso_prepare_transfer.config import Config
from meso_prepare_transfer.utils.sync_dataset import Sync


def parse_platform_json(
    data_directory: Path,
) -> tuple[str, str]:
    """Parse platform.json to get subject and project ID.

    Raises:
        FileNotFoundError: If platform.json is not found.
        KeyError: If the platform.json data isn't formatted as expected.
    """
    platform_fp = next(data_directory.rglob("*platform.json"), "")
    logger.debug(f"Parsing platform.json for subject and project ID at {platform_fp}")
    if not platform_fp:
        raise FileNotFoundError(f"No platform.json found in {data_directory}")
    with open(platform_fp, "r") as pf:
        platform_data = json.load(pf)
    subject_id = platform_data["subject_id"]
    project_id = platform_data["project_code"]
    return subject_id, project_id


def get_start_end_times(data_directory: Path) -> tuple[datetime, datetime]:
    """Gets the start and end times from the sync file based
    on the stimulus trigger line (rising edge for start, falling edge for end)

    Returns
    -------
    tuple
        (start_time: datetime, end_time: datetime)
    """
    sync_file = [i for i in data_directory.glob("*.h5") if "full_field" not in str(i)][0]
    logger.debug(f"Parsing sync file for start and end times at {sync_file}")
    sync_data = Sync(sync_file)
    sync_start = sync_data.meta_data["start_time"]
    acq_start = sync_data.get_rising_edges(5, units="seconds")  # stimulus trigger line
    acq_end = sync_data.get_falling_edges(5, units="seconds")  # stimulus trigger line
    if not acq_start or not acq_end:
        raise ValueError("Could not pull rising or falling edge from line 5 in sync file")
    if len(acq_start) > 1 or len(acq_end) > 1:
        raise ValueError("Multiple rising or falling edges detected")
    return sync_start + timedelta(seconds=acq_start[0]), sync_start + timedelta(seconds=acq_end[0])


def generate_aind_metadata(
    data_directory: Path,
    behavior_dir: Path,
    session_id: str,
    user_name: str,
    subject_id: str,
    project_id: str,
    data_schema_project_name: str,
    start_time: str,
    end_time: str,
    config: Config,
) -> tuple[dict, dict]:
    """Generates aind-data-schema compliant session.json and data_description.csv"""
    logger.info("Generating Session Json")

    session_metadata = JobSettings(
        input_source=data_directory,
        behavior_source=behavior_dir,
        session_id=session_id,
        output_directory=data_directory,
        session_start_time=start_time,
        session_end_time=end_time,
        subject_id=subject_id,
        project=project_id,
        experimenter_full_name=[user_name],
        optional_output=data_directory,
    )
    meso_etl = MesoscopeEtl(session_metadata)
    meso_etl.run_job()

    logger.info("Generating Data Description Json")
    investigators = [PIDName(name=inv) for inv in config.investigators[data_schema_project_name]]

    raw_description = RawDataDescription(
        modality=[Modality.POPHYS, Modality.BEHAVIOR_VIDEOS, Modality.BEHAVIOR],
        platform=Platform.MULTIPLANE_OPHYS,
        subject_id=subject_id,
        creation_time=start_time,
        institution=Organization.AIND,
        investigators=investigators,
        funding_source=[Funding(funder=Organization.AI)],
        project_name=data_schema_project_name,
        data_summary=project_id,
    )
    raw_description_json = raw_description.model_dump_json()
    raw_description_revalidated = RawDataDescription.model_validate_json(raw_description_json)
    raw_description_revalidated.write_standard_file(output_directory=data_directory)

    return session_metadata, raw_description_revalidated


def search_files(
    base_directory: Path,
    patterns: list[str],
    extra_search_key: str = "",
) -> list[str]:
    """Search for files in base_directory matching any of the glob patterns.

    Parameters
    ----------
    base_directory : Path
        The directory to search within.
    patterns : list[str]
        List of glob patterns to match files.
    extra_search_key : str, optional
        An additional string that must be present in the file path, by default ""

    Returns
    -------
    list[str]
        List of matching file paths as strings.
    """
    matched_files = []
    for pattern in patterns:
        for file_path in base_directory.rglob(pattern):
            if extra_search_key in str(file_path):
                matched_files.append(str(file_path))
    return matched_files


def generate_watchdog_manifest(
    session_id: str,
    subject_id: str,
    project_name: str,
    user_full_name: str,
    start_time: datetime,
    config: Config,
) -> None:
    """Generates a manifest file for aind-watchdog-service to transfer data off-rig"""
    logger.info("Generating manifest file")
    data_directory = config.acquisition_dir / session_id

    data = {}
    data[Modality.POPHYS.abbreviation] = search_files(data_directory, config.modalities["pophys"])
    data[Modality.BEHAVIOR.abbreviation] = search_files(data_directory, config.modalities["behavior"])
    data[Modality.BEHAVIOR_VIDEOS.abbreviation] = search_files(
        config.behavior_video_dir,
        config.modalities["behavior-videos"],
        extra_search_key=data_directory.name,
    )
    schemas = []
    for i in config.schemas:
        # If schema is not a file, that exists, pull it from the data directory
        if Path(i).is_file():
            schemas.append(i)
        else:
            schemas.append(data_directory / i)

    manifest_file = ManifestConfig(
        processor_full_name=user_full_name,
        subject_id=subject_id,
        acquisition_datetime=start_time,
        modalities=data,
        schemas=[str(s) for s in schemas],
        project_name=project_name,
        extra_identifying_info={"ophys_session_id": session_id},
        **config.watchdog_manifest_kwargs,
    )
    manifest_path = manifest_file.write_standard_file(config.manifest_directory)
    logger.info(f"Manifest written to {manifest_path}")


@logger.catch(message="Could not process dataset", onerror=lambda _: sys.exit(1))
def process_dataset(user_name: str, session_id: str, config: Config) -> bool:
    """Process a single dataset: generate metadata and manifest files."""
    logger.info("Processing dataset")

    subject_id, project_id = parse_platform_json(config.acquisition_dir / session_id)

    with logger.contextualize(subject_id=subject_id, project_id=project_id):
        data_directory = config.acquisition_dir / session_id

        camera_jsons = list(config.behavior_video_dir.glob(f"{session_id}*.json"))
        if len(camera_jsons) == 0:
            logger.error("No camera json files found")
            return False
        elif len(camera_jsons) < 3:
            logger.info("Less than 3 camera jsons found")

        start_time, end_time = get_start_end_times(data_directory)

        if "OpenScope" in project_id:
            data_schema_project_name = "OpenScope"
        else:
            data_schema_project_name = "Learning mFISH-V1omFISH"

        generate_aind_metadata(
            data_directory=data_directory,
            behavior_dir=Path(config.behavior_video_dir),
            session_id=session_id,
            user_name=user_name,
            subject_id=subject_id,
            project_id=project_id,
            data_schema_project_name=data_schema_project_name,
            start_time=start_time,
            end_time=end_time,
            config=config,
        )

        generate_watchdog_manifest(
            session_id,
            subject_id,
            data_schema_project_name,
            user_name,
            start_time,
            config,
        )
        return True
