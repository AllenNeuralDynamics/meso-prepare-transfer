from datetime import datetime
from pathlib import Path
import yaml

import pytest

from meso_prepare_transfer.business_logic import process_dataset
from meso_prepare_transfer.config import Config
from tests.dummy_data import make_dummy_dataset


@pytest.mark.parametrize(
    "project",
    [
        "OpenScope",
        "Learning mFISH-V1omFISH",
        "SomeOtherProject",
    ],
)
def test_prepare_transfer(caplog, tmpdir, mocker, project):
    """Test the prepare transfer process with a dummy dataset"""
    acquisition_dir = Path(tmpdir) / "acquisition_data"
    behavior_dir = Path(tmpdir) / "behavior_videos"
    watchdog_manifest_dir = Path(tmpdir) / "manifests"
    watchdog_manifest_dir.mkdir(parents=True, exist_ok=True)
    subject_id = "614173"
    project_code = project
    session_id = "20000001"

    # Create dummy dataset
    make_dummy_dataset(
        acquisition_dir=acquisition_dir,
        behavior_video_dir=behavior_dir,
        subject_id=subject_id,
        project_code=project_code,
        session_id=session_id,
    )

    config = Config(
        acquisition_dir=acquisition_dir,
        behavior_video_dir=behavior_dir,
        logserver_url="",
        manifest_directory=watchdog_manifest_dir,
    )

    mocker.patch(
        "meso_prepare_transfer.business_logic.get_start_end_times",
        return_value=(datetime(2023, 1, 1, 12, 0, 0), datetime(2023, 1, 1, 13, 0, 0)),
    )

    mocker.patch("aind_metadata_mapper.mesoscope.session.MesoscopeEtl.__init__", return_value=None)
    mocker.patch("aind_metadata_mapper.mesoscope.session.MesoscopeEtl.run_job", return_value=None)

    process_dataset("User Name", session_id, config)

    assert (acquisition_dir / session_id / "session.json").exists()
    assert (acquisition_dir / session_id / "data_description.json").exists()

    assert len(list(watchdog_manifest_dir.glob("*manifest*"))) == 1

    manifest = list(watchdog_manifest_dir.glob("*manifest*"))[0]
    manifest_contents = yaml.safe_load(manifest.read_text())

    assert manifest_contents["modalities"].keys() == config.modalities.keys()

    schemas = [Path(s) for s in manifest_contents["schemas"]]
    assert acquisition_dir / session_id / "session.json" in schemas
    assert acquisition_dir / session_id / "data_description.json" in schemas

    assert manifest_contents["project_name"] in ["OpenScope", "Learning mFISH-V1omFISH"]
