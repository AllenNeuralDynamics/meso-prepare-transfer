from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.platforms import Platform
from pydantic import BaseModel, Field, field_validator


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
    schedule_time: Optional[datetime] = Field(
        default=None,
        description="Transfer time to schedule copy and upload, defaults to immediately",
        title="APScheduler transfer time",
    )
    transfer_endpoint: str = Field(
        default="vast", description="Transfer endpoint", title="Transfer endpoint"
    )
    force_cloud_sync: Optional[bool] = Field(
        default=False, description="Force cloud sync", title="Force cloud sync"
    )
    s3_bucket: str = Field(
        default="private", description="s3 endpoint", title="S3 endpoint"
    )
    destination: str = Field(
        description="where to send data to on VAST",
        title="Destination dierctory",
    )
    capsule_id: Optional[str] = Field(
        description="Capsule ID of pipeline to run", title="Capsule"
    )
    mount: Optional[str] = Field(
        description="Mount point of the data", title="Mount point"
    )
    modalities: Dict[str, List[str]] = Field(
        description="list of ModalityFile objects containing modality names and associated files",
        title="modality files",
    )
    schemas: list = Field(description="list of schema files", title="schema files")
    project_name: str = Field(description="Project name", title="Project name")
    processor_full_name: str = Field(
        description="Processor full name", title="Processor full name"
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

    @field_validator("destination")
    @classmethod
    def verify_destination(cls, data: str) -> str:
        if Path(data).exists():
            return data
        else:
            raise ValueError(f"{data} does not exist")

    @field_validator("schemas")
    @classmethod
    def verify_schemas(cls, data: list) -> list:
        for schema in data:
            if not Path(schema).exists():
                raise ValueError(f"{schema} does not exist")
        return data
