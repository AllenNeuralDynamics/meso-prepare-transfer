from pydantic import Field, BaseModel
from datetime import datetime
from pathlib import Path
from typing import List


class UserInput(BaseModel):
    """Data to be entered by the user."""

    # TODO: for now this will need to be directly input by the user.
    #  In the future, the workflow sequencing engine should be able to put
    #  this in a json or we can extract it from SLIMS
    input_source: Path
    behavior_source: Path
    output_directory: Path
    session_start_time: datetime
    session_end_time: datetime
    subject_id: str
    project: str
    experimenter_full_name: List[str] = Field(..., title="Full name of the experimenter")
