from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from aind_data_schema_models import modalities, platforms
from pydantic import BaseModel, Field, field_validator

Platform = Literal[tuple(set(platforms.Platform.abbreviation_map.keys()))]
Modality = Literal[tuple(set(modalities.Modality.abbreviation_map.keys()))]


class ModalityMapConfig(BaseModel):
    """Template to verify all files that need to be uploaded"""

    name: str = Field(
        description="Unique name for session data assets. Should follow AINDs schema for naming data assets",
        title="Unique name",
    )
    platform: Platform = Field(description="Platform type", title="Platform type")
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
    modalities: Dict[Modality, List[str]] = Field(
        description="list of ModalityFile objects containing modality names and associated files",
        title="modality files",
    )
    schemas: list = Field(description="list of schema files", title="schema files")
    project_name: str = Field(description="Project name", title="Project name")
    processor_full_name: str = Field(
        description="Processor full name", title="Processor full name"
    )
    extra_identifying_info: Optional[dict] = None

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

    @field_validator("modalities", mode="before")
    @classmethod
    def normalize_modalities(cls, value) -> Dict[Modality, List[str]]:
        """Normalize modalities"""
        if isinstance(value, dict):
            _ret: Dict[str, Any] = {}
            for modality, v in value.items():
                if isinstance(modality, getattr(modalities.Modality, "ALL")):
                    key = getattr(modality, "abbreviation", None)
                    if key is None:
                        _ret[modality] = v
                    else:
                        _ret[key] = v
                else:
                    _ret[modality] = v
            return _ret
        else:
            return value

    @field_validator("platform", mode="before")
    @classmethod
    def normalize_platform(cls, value) -> Platform:
        """Normalize modalities"""
        if isinstance(value, getattr(platforms.Platform, "ALL")):
            ret = getattr(value, "abbreviation", None)
            return ret if ret else value
        else:
            return value
