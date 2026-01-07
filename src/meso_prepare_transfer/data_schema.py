from pathlib import Path
import json

from aind_data_schema.core.data_description import Funding, RawDataDescription
from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.platforms import Platform
from aind_data_transfer_models.core import BucketType
from aind_metadata_mapper.mesoscope.models import JobSettings
from aind_metadata_mapper.mesoscope.session import MesoscopeEtl

from loguru import logger

from meso_prepare_transfer.config import Config


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
