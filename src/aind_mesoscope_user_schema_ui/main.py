# This Python file uses the following encoding: utf-8
import json
import logging
import os
import sys
from datetime import datetime as dt
from datetime import timedelta
from pathlib import Path
from typing import Union

import requests
import yaml
from aind_data_schema.core.data_description import Funding, RawDataDescription
from aind_data_schema_models.modalities import Modality
from aind_data_schema_models.organizations import Organization
from aind_data_schema_models.pid_names import PIDName
from aind_data_schema_models.platforms import Platform
from aind_data_transfer_models.core import BucketType
from aind_metadata_mapper.mesoscope.models import JobSettings
from aind_metadata_mapper.mesoscope.session import MesoscopeEtl
from PySide6.QtWidgets import QApplication, QWidget

from aind_mesoscope_user_schema_ui.logging_config import setup_logging
from aind_mesoscope_user_schema_ui.models.config import ModalityMapConfig
from aind_mesoscope_user_schema_ui.sync_dataset import Sync

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py
from aind_mesoscope_user_schema_ui.ui.ui_form import UiUserSettings


class Widget(QWidget):
    _LIMS_URLS = {
        "session": "http://lims2/ophys_sessions.json?id={}",
    }
    _INVESTIGATORS = {
        "Learning mFISH-V1omFISH": [
            PIDName(name="Marina Garrett"),
            PIDName(name="Peter Groblewski"),
            PIDName(name="Anton Arkhipov"),
            PIDName(name="Omid Zobeiri"),
        ],
        "OpenScope": [PIDName(name="Jerome Lecoq")],
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiUserSettings()
        self.ui.setupUi(self)
        self.connect_signals()
        config_fp = os.getenv("MESO_USER_SETTING_CONFIG")
        self.config = self._read_yaml(config_fp)
        self.error = []
        self._setup_logging()

    def connect_signals(self) -> None:
        """Connect signals to slots."""
        self.ui.submitPushButton.setEnabled(False)
        self.ui.submitPushButton.clicked.connect(self.submit_button_clicked)
        self.ui.userNameLineEdit.textChanged.connect(self.check_submit_button)
        self.ui.sessionIdLineEdit.textChanged.connect(self.check_submit_button)

    def _setup_logging(self, log_dir: Path = None) -> None:
        if not log_dir:
            log_dir = Path(".")
        if not log_dir.exists():
            log_dir.mkdir(parents=True)
        setup_logging(log_file=log_dir / "prepare_transfer.log")

    def _read_yaml(self, file_path: str) -> dict:
        """loads and returns yaml file contents as dict

        Parameters
        ----------
        file_path : str
            path to configuration

        Returns
        -------
        dict
            config data
        """
        with open(file_path, "rb") as file:
            return yaml.safe_load(file)

    def _get_lims_response(self, lims_entry: str, api: str) -> requests.Response:
        """Returns lims response.

        Parameters
        ----------
        lims_entry : str
            LIMS entry.

        Returns
        -------
        requests.Response
        """
        return requests.get(self._LIMS_URLS[api].format(lims_entry), timeout=2)

    def _check_user(self, user_name: str) -> bool:
        """verify there are two components to the string of the user input

        Parameters
        ----------
        user_name: str
            User name from line edit

        Returns
        -------
        bool
            truth
        """
        if not " " in user_name:
            return False
        else:
            return True

    def _session_data(self, session_response: requests.Response) -> Union[bool, dict]:
        """Validates lims session

        Parameters
        ----------
        session_resposne: requests.Response

        Returns
        -------
        Union[bool, dict]
            session data or resposne
        """
        try:
            session_data = session_response.json()[0]
        except IndexError:
            self.ui.error_message.showMessage("Invalid session ID")
        try:
            assert session_data
            return session_data
        except AssertionError:
            return False

    def _project_and_mouse_id(self, session_data: dict) -> tuple:
        """returns project id and mouse id from session data

        Parameters
        ----------
        session_data : dict
            session data from lims response

        Returns
        -------
        tuple
            (subject id, project id)
        """
        subject_id = session_data["specimen"]["external_specimen_name"]
        project_id = session_data["project"]["code"]
        return subject_id, project_id

    def _behavior_cameras(self, session_id: str) -> Union[bool, dict]:
        """_summary_

        Parameters
        ----------
        session_id : str
            session id to glob for metadata

        Returns
        -------
        Union[bool, dict]
            camera metadata or false
        """
        camera_json = [
            c for c in Path(self.config["behavior_dir"]).glob(f"{session_id}*.json")
        ]
        if len(camera_json) < 3:
            logging.info("Less than 3 camera jsons found")
        if len(camera_json) == 0:
            return False
        with open(camera_json[0], "rb") as j:
            return json.load(j)

    def _generate_user_settings(
        self,
        start_time: str,
        end_time: str,
        subject_id: str,
        project_id: str,
        session_id: str,
        user_name: str,
    ) -> dict:
        """_Generates user settings json for metdata mapping into session json

        Parameters
        ----------
        start_time : str
            acquisition start time (according to behavior cams)
        end_time : str
            acquisition end time (according to behavior cams)
        subject_id : str
            mouse id
        project_id : str
            project associated with session
        session_id : str
            session id
        user_name: str
            full name of user
        """
        logging.info("Generating user settings")
        user_input = JobSettings(
            input_source=self.config["acquisition_dir"] + "/" + session_id,
            behavior_source=self.config["behavior_dir"],
            session_id=session_id,
            output_directory=self.config["acquisition_dir"] + "/" + session_id,
            session_start_time=start_time,
            session_end_time=end_time,
            subject_id=subject_id,
            project=project_id,
            experimenter_full_name=[user_name],
            optional_output=self.config["acquisition_dir"] + "/" + session_id,
        )
        meso_etl = MesoscopeEtl(user_input)
        meso_etl.run_job()
        return user_input.model_dump()

    def _generate_data_description(
        self,
        subject_id: str,
        start_time: str,
        organization: Organization,
        investigators: list,
        funding_source: list,
        session_id: str,
        project: str,
        project_id: str,
    ) -> dict:
        """Generate data description for session

        Parameters
        ----------
        subject_id : str
            mouse id
        start_time : str
            acquisition start time
        organization : Organization
            organization
        investigators : list
            list of investigators
        funding_source : list
            list of funding sources
        session_id : str
            session id
        project : str
            project name
        project_id : str
            project id

        Returns
        -------
        dict
            data description
        """

        raw_description = RawDataDescription(
            modality=[Modality.POPHYS, Modality.BEHAVIOR_VIDEOS],
            platform=Platform.MULTIPLANE_OPHYS,
            subject_id=subject_id,
            creation_time=start_time,
            institution=organization,
            investigators=investigators,
            funding_source=funding_source,
            project_name=project,
            data_summary=project_id,
        )
        serialized = raw_description.model_dump_json()
        deserialized = RawDataDescription.model_validate_json(serialized)
        deserialized.write_standard_file(
            output_directory=self.config["acquisition_dir"] + "/" + session_id,
        )
        return json.loads(serialized)

    def _search_files(self, directory: str, files: list, extra_search_key=None) -> dict:
        """searches for files in a directory

        Parameters
        ----------
        directory : str
            directory to search
        files : dict
            files to search for
        extra_search_key : str
            Only for behavior files since they are not in any subdirectory
        Returns
        -------
        dict
            found files
        """
        found_files = []
        for file in files:
            if extra_search_key:
                file = extra_search_key + file
            src = list(Path(directory).glob(file))
            if len(src) > 1:
                for i in src:
                    found_files.append(str(i))
            elif len(src) == 1:
                found_files.append(str(src[0]))
            else:
                self.error.append(file)
        if len(found_files) == 0:
            self.ui.error_message.showMessage(f"No files found in {directory}")
        return found_files

    def get_start_end_times(self, sync_file: Path) -> tuple:
        """Gets the start and end times from the sync file based
        on the stimulus trigger line (rising edge for start, falling edge for end)

        Returns
        -------
        tuple
            (start_time: datetime, end_time: datetime)
        """
        sync_data = Sync(sync_file)
        sync_start = sync_data.meta_data["start_time"]
        acq_start = sync_data.get_rising_edges(
            5, units="seconds"
        )  # stimulus trigger line
        acq_end = sync_data.get_falling_edges(5, units="seconds")  # stimulus trigger line
        if not acq_start or not acq_end:
            raise ValueError(
                "Could not pull rising or falling edge from line 5 in sync file"
            )
        if len(acq_start) > 1 or len(acq_end) > 1:
            raise ValueError("Multiple rising or falling edges detected")
        return sync_start + timedelta(seconds=acq_start[0]), sync_start + timedelta(
            seconds=acq_end[0]
        )

    def _generate_manifest_file(
        self, user_input: dict, data_description: dict, session_id: str
    ) -> None:
        """use information from user input to generate yaml file

        Parameters
        ----------
        user_input : dict
            user input data
        data_description : dict
            data description information
        session_id: str
            session id
        """
        logging.info("Generating manifest file")
        platform = self.config["platform"]
        name = (
            platform.replace("_", "-")
            + "_"
            + user_input["subject_id"]
            + "_"
            + dt.now().strftime("%Y-%m-%d_%H-%M-%S")
        )
        data_directory = Path(self.config["acquisition_dir"]) / session_id
        sync_file = [
            i for i in data_directory.glob("*.h5") if "full_field" not in str(i)
        ][0]
        start_time, _ = self.get_start_end_times(sync_file)
        acquisition_dir = Path(user_input["input_source"])
        behavior_dir = Path(user_input["behavior_source"])
        manifests = {}
        manifests[Modality.POPHYS] = self._search_files(
            acquisition_dir, self.config["modalities"]["ophys"]
        )  # TODO: this should be a parameter
        manifests[Modality.BEHAVIOR] = self._search_files(
            acquisition_dir, self.config["modalities"]["behavior"]
        )
        manifests[Modality.BEHAVIOR_VIDEOS] = self._search_files(
            behavior_dir,
            self.config["modalities"]["behavior-videos"],
            extra_search_key=acquisition_dir.name,
        )  # TODO: this should be a parameter
        if self.error:
            self.ui.error_message.showMessage(f"Files not found: {self.error}")
            self.error = []
        schemas = []
        for i in self.config["schemas"]:
            # If schema is not a file, that exists, pull it from the data directory
            if Path(i).is_file():
                schemas.append(i)
            else:
                schemas.append(os.path.join(user_input["input_source"], i))
        manifest_file = dict(
            name=name,
            platform=Platform.MULTIPLANE_OPHYS,
            processor_full_name=user_input["experimenter_full_name"][0],
            subject_id=user_input["subject_id"],
            acquisition_datetime=start_time,
            schedule_time=dt.now().replace(hour=3, minute=0, second=0, microsecond=0)
            + timedelta(days=1),
            s3_bucket=self.config["s3_bucket"],
            destination=self.config["destination"],
            capsule_id=self.config["capsule_id"],
            mount=self.config["mount"],
            modalities=manifests,
            schemas=schemas,
            project_name=data_description["project_name"],
            transfer_endpoint=self.config["transfer_endpoint"],
            force_cloud_sync=self.config["force_cloud_sync"],
        )
        modality_map = ModalityMapConfig(**manifest_file)
        if not Path(self.config["manifest_directory"]).exists():
            Path(self.config["manifest_directory"]).mkdir()
        with open(
            Path(self.config["manifest_directory"])
            / f"manifest_{dt.now().strftime('%Y%m%d%H%M%S')}.yml",
            "w",
        ) as yam:
            yaml.safe_dump(
                modality_map.model_dump(),
                yam,
                default_flow_style=False,
                allow_unicode=True,
            )
        logging.info("Manifest generated %s", self.config["manifest_directory"])

    def submit_button_clicked(self) -> None:
        """Runs job to retrieve data from user inputs.
        If successful will drop a UserSettings.json in the acquisition directory.
        """
        logging.info("Submit button clicked")
        user_name = self.ui.userNameLineEdit.text()
        session_id = self.ui.sessionIdLineEdit.text()
        logging.info(f"User name: {user_name}, Session ID: {session_id}")
        if not self._check_user(user_name):
            self.ui.error_message.showMessage("Enter a valid user name")
            return
        session_response = self._get_lims_response(session_id, "session")
        session_data = self._session_data(session_response)
        if not session_data:
            self.ui.error_message.showMessage("Invalid session ID")
            return
        subject_id, project_id = self._project_and_mouse_id(session_data)
        logging.info(f"Project ID: {project_id}, Subject ID: {subject_id}")
        behavior_data = self._behavior_cameras(session_id)
        if not behavior_data:
            self.ui.error_message.showMessage(
                "No camera metadata found: contact engineering"
            )
            return
        data_directory = Path(self.config["acquisition_dir"]) / session_id
        sync_file = [
            i for i in data_directory.glob("*.h5") if "full_field" not in str(i)
        ][0]
        start_time, end_time = self.get_start_end_times(sync_file)
        user_input = self._generate_user_settings(
            start_time, end_time, subject_id, project_id, session_id, user_name
        )
        logging.info("Project ID %s", project_id)
        if "OpenScope" in project_id:
            project_id = project_name = "OpenScope"
        else:
            project_name = "Learning mFISH-V1omFISH"
        data_description = self._generate_data_description(
            subject_id,
            start_time,
            Organization.AIND,
            self._INVESTIGATORS[project_name],
            [Funding(funder=Organization.AI)],
            session_id,
            project_name,
            project_id,
        )
        self._generate_manifest_file(user_input, data_description, session_id)
        self.ui.error_message.showMessage("User settings saved")
        self.ui.userNameLineEdit.clear()
        self.ui.sessionIdLineEdit.clear()

    def check_submit_button(self) -> None:
        """Checks conditions to see if the submit button can be enabled."""
        if self.ui.userNameLineEdit.text() and self.ui.sessionIdLineEdit.text():
            self.ui.submitPushButton.setEnabled(True)
        else:
            self.ui.submitPushButton.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
