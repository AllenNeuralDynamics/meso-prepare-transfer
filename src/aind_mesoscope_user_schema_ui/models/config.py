from pydantic import Field, BaseModel, field_validator
from datetime import datetime
from typing import List, Dict, Optional
from aind_data_schema.models.modalities import Modality
from aind_data_schema.models.platforms import Platform


class ModalityMapConfig(BaseModel):
    """Template to verify all files that need to be uploaded"""

    name: str = Field(
        description="Unique name for session data assets. Should follow AINDs schema for naming data assets",
        title="Unique name",
    )
    platform: str = Field(description="Platform type", title="Platform type")
    subject_id: int = Field(description="Subject ID", title="Subject ID")
    acquisition_datetime: datetime = Field(
        title="Acquisition datetime",
    )
    transfer_time: Optional[str] = Field(default="now",
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

    @field_validator("modalities")
    @classmethod
    def verify_modality(cls, data: Dict[str, List[str]]) -> Dict[str, List[str]]:
        for key in data.keys():
            if key.lower() not in Modality._abbreviation_map:
                raise ValueError(f"{key} not in accepted modalities")
        return data

    @field_validator("platform")
    @classmethod
    def verify_platform(cls, data: str) -> str:
        if "_" in data:
            data = data.replace("_", "-")
        if data.lower() not in Platform._abbreviation_map:
            raise ValueError(f"{data} not in accepted platforms")
        return data

    @field_validator("transfer_time", mode="after")
    @classmethod
    def verify_datetime(cls, data: str) -> str:
        try:
            datetime.strptime(data, "%H:%M").time()
        except ValueError:
            raise ValueError(f"Specify time in HH:MM format, not {data}")
        return data
