from pydantic import Field, BaseModel, field_validator
from datetime import datetime
from typing import List, Dict, Optional
from aind_data_schema.models.modalities import Modality
from aind_data_schema.models.platforms import Platform


class UserInput(BaseModel):
    """Data to be entered by the user."""

    # TODO: for now this will need to be directly input by the user.
    #  In the future, the workflow sequencing engine should be able to put
    #  this in a json or we can extract it from SLIMS
    input_source: str
    behavior_source: str
    output_directory: str
    session_start_time: str
    session_end_time: str
    subject_id: str
    project: str
    experimenter_full_name: List[str] = Field(..., title="Full name of the experimenter")


class ModalityMapConfig(BaseModel):
    """Template to verify all files that need to be uploaded"""

    name: str = Field(
        description="Unique name for session data assets. Should follow AINDs schema for naming data assets",
        title="Unique name",
    )
    platform: str = Field(description="Platform type", title="Platform type")
    subject_id: int = Field(description="Subject ID", title="Subject ID")
    acquisition_datetime: str = Field(
        description="acquisition datetime in YYYY-MM-DD HH:mm:ss format",
        title="Acquisition datetime",
    )
    transfer_time: Optional[str] = Field(
        default="23:00",
        description="Transfer time to schedule copy and upload, defaults to immediately",
        title="APScheduler transfer time",
    )
    s3_bucket: str = Field(description="s3 endpoint", title="S3 endpoint")
    destination: str = Field(
        description="where to send data to on VAST",
        title="VAST destination and maybe S3?",
    )
    capsule_id: Optional[str] = Field(
        description="Capsule ID of pipeline to run", title="Capsule"
    )
    modalities: Dict[str, List[str]] = Field(
        description="list of ModalityFile objects containing modality names and associated files",
        title="modality files",
    )

    @field_validator("transfer_time")
    def verify_datetime(cls, data: str) -> str:
        try:
            datetime.strptime(data, "%H:%M").time()
        except ValueError:
            raise ValueError(f"Specify time in HH:MM format, not {data}")
        return data
