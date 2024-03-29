# This Python file uses the following encoding: utf-8
import sys
import requests
from pathlib import Path
import yaml
import json
import os
from typing import Union
from PySide6.QtWidgets import QApplication, QWidget

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py
from aind_mesoscope_user_schema_ui.ui.ui_form import UiUserSettings
from aind_mesoscope_user_schema_ui.config import UserInput


class Widget(QWidget):
    _LIMS_URLS = {
        "session": "http://lims2/ophys_sessions.json?id={}",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiUserSettings()
        self.ui.setupUi(self)
        self.connect_signals()
        config_fp = os.getenv("MESO_USER_SETTING_CONFIG")
        self.config = self.get_config(config_fp)

    def connect_signals(self) -> None:
        """Connect signals to slots."""
        self.ui.submitPushButton.setEnabled(False)
        self.ui.submitPushButton.clicked.connect(self.submit_button_clicked)
        self.ui.userNameLineEdit.textChanged.connect(self.check_submit_button)
        self.ui.sessionIdLineEdit.textChanged.connect(self.check_submit_button)

    def get_config(self, file_path: str) -> dict:
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
        session_data = session_response.json()[0]
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
            print("Less than 3 camera jsons found")
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
    ) -> None:
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
        user_input = UserInput(
            input_source=self.config["acquisition_dir"],
            behavior_source=self.config["behavior_dir"],
            output_directory=self.config["output_dir"],
            session_start_time=start_time,
            session_end_time=end_time,
            subject_id=subject_id,
            project=project_id,
            experimenter_full_name=[user_name],
        )
        user_input = user_input.dict()
        with open(
            Path(self.config["acquisition_dir"]) / session_id / "user_settings.json",
            "w",
        ) as j:
            json.dump(user_input, j, indent=4)

    def submit_button_clicked(self) -> None:
        """Runs job to retrieve data from user inputs.
        If successful will drop a UserSettings.json in the acquisition directory.
        """
        print("Submit button clicked")
        user_name = self.ui.userNameLineEdit.text()
        session_id = self.ui.sessionIdLineEdit.text()
        if not self._check_user(user_name):
            self.ui.error_message.showMessage("Enter a valid user name")
            return
        session_response = self._get_lims_response(session_id, "session")
        session_data = self._session_data(session_response)
        if not session_data:
            self.ui.error_message.showMessage("Invalid session ID")
            return
        subject_id, project_id = self._project_and_mouse_id(session_data)
        behavior_data = self._behavior_cameras(session_id)
        if not behavior_data:
            self.ui.error_message.showMessage(
                "No camera metadata found: contact engineering"
            )
            return
        start_time = behavior_data["RecordingReport"]["TimeStart"]
        end_time = behavior_data["RecordingReport"]["TimeEnd"]
        self._generate_user_settings(
            start_time, end_time, subject_id, project_id, session_id, user_name
        )
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
