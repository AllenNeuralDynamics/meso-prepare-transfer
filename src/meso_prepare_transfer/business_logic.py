"""Functions to process a mesoscope dataset for transfer off-rig"""

from datetime import datetime, timedelta
import requests
from pathlib import Path
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


# # TODO: Remove
# @logger.catch()
# def query_lims(
#     session_id: str,
#     session_endpoint: str,
# ) -> tuple[str, str]:
#     """Query LIMS for subject and project ID based on session ID.

#     Raises:
#         requests.exceptions.RequestException: If the HTTP request fails.
#         IndexError: If the session id is invalid and no data is found in LIMS.
#         KeyError: If the LIMS session data isn't formatted as expected.
#     """
#     url = session_endpoint.format(session_id)
#     response = requests.get(url, timeout=2)
#     response.raise_for_status()
#     try:
#         session_data = response.json()[0]
#     except IndexError:
#         raise IndexError("No data found for the given session ID.")
#     subject_id = session_data["specimen"]["external_specimen_name"]
#     project_id = session_data["project"]["code"]
#     return subject_id, project_id


@logger.catch()
def parse_platform_json(
    data_directory: Path,
) -> tuple[str, str]:
    """Parse platform.json to get subject and project ID.

    Raises:
        FileNotFoundError: If platform.json is not found.
        KeyError: If the platform.json data isn't formatted as expected.
    """
    platform_fp = next(data_directory.rglob("*platform.json"), "")
    if not platform_fp:
        raise FileNotFoundError(f"No platform.json found in {data_directory}")
    with open(platform_fp, "r") as pf:
        platform_data = json.load(pf)
    subject_id = platform_data["subject_id"]
    project_id = platform_data["project_code"]
    return subject_id, project_id


@logger.catch()
def get_start_end_times(data_directory: Path) -> tuple[datetime, datetime]:
    """Gets the start and end times from the sync file based
    on the stimulus trigger line (rising edge for start, falling edge for end)

    Returns
    -------
    tuple
        (start_time: datetime, end_time: datetime)
    """
    sync_file = [i for i in data_directory.glob("*.h5") if "full_field" not in str(i)][0]
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

    # session_json_contents = session_metadata.model_dump()

    if "OpenScope" in project_id:
        data_schema_project_name = "OpenScope"
    else:
        data_schema_project_name = "Learning mFISH-V1omFISH"

    investigators = [PIDName(name=inv) for inv in config.investigators[data_schema_project_name]]

    raw_description = RawDataDescription(
        modality=[Modality.POPHYS, Modality.BEHAVIOR_VIDEOS, Modality.BEHAVIOR],
        platform=Platform.MULTIPLANE_OPHYS,
        subject_id=subject_id,
        creation_time=start_time,
        institution=Organization.AIND,
        investigators=investigators,
        funding_source=[Funding(funder=Organization.AIND)],
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


@logger.catch()
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
    # sync_file = [i for i in data_directory.glob("*.h5") if "full_field" not in str(i)][0]
    # start_time, _ = self.get_start_end_times(sync_file)
    # name = platform.replace("_", "-") + "_" + user_input["subject_id"] + "_" + start_time.strftime("%Y-%m-%d_%H-%M-%S")
    # acquisition_dir = Path(user_input["input_source"])
    # behavior_dir = Path(user_input["behavior_source"])
    data = {}
    data[Modality.POPHYS.abbreviation] = search_files(data_directory, config.modalities["pophys"])
    data[Modality.BEHAVIOR.abbreviation] = search_files(data_directory, config.modalities["behavior"])
    data[Modality.BEHAVIOR_VIDEOS.abbreviation] = search_files(
        config.behavior_video_dir,
        config.modalities["behavior-videos"],
        extra_search_key=data_directory.name,
    )
    # if self.error:
    #     self.ui.error_message.showMessage(f"Files not found: {self.error}")
    #     self.error = []
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
        schemas=schemas,
        project_name=project_name,
        extra_identifying_info={"ophys_session_id": session_id},
        **config.watchdog_manifest_kwargs,
    )
    manifest_file.write_standard_file(config.manifest_directory)


def process_dataset(user_name: str, session_id: str, config: Config) -> bool:
    """Process a single dataset: generate metadata and manifest files."""
    logger.info("Processing dataset", session_id=session_id, user_name=user_name)

    # subject_id, project_id = query_lims(session_id, config.session_endpoint)
    subject_id, project_id = parse_platform_json(config.acquisition_dir / session_id)

    logger.info(f"Project ID: {project_id}, Subject ID: {subject_id}")

    # behavior_data = behavior_camera_data(session_id, Path(config.behavior_dir))
    # behavior_data = self._behavior_cameras(session_id)
    # if not behavior_data:
    #     logger.error("No camera metadata found: contact engineering")
    #     self.ui.error_message.showMessage("No camera metadata found: contact engineering")
    #     return
    data_directory = config.acquisition_dir / session_id

    camera_jsons = list(config.behavior_video_dir.glob(f"{session_id}*.json"))
    if len(camera_jsons) == 0:
        logger.error("No camera json files found")
        return False
    elif len(camera_jsons) < 3:
        logger.info("Less than 3 camera jsons found")

    start_time, end_time = get_start_end_times(data_directory)

    generate_aind_metadata(
        data_directory=data_directory,
        behavior_dir=Path(config.behavior_video_dir),
        session_id=session_id,
        user_name=user_name,
        subject_id=subject_id,
        project_id=project_id,
        start_time=start_time,
        end_time=end_time,
        config=config,
    )

    generate_watchdog_manifest(
        session_id,
        subject_id,
        project_id,
        user_name,
        start_time,
        config,
    )
    return True
