# This Python file uses the following encoding: utf-8
import sys
import requests
from pathlib import Path
import yaml
import json

from PySide6.QtCore import QMetaMethod
from PySide6.QtWidgets import QApplication, QWidget

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py
from ui.ui_form import UiUserSettings
from config import UserInput


class Widget(QWidget):
    _LIMS_URLS = {
        "user": "http://lims2/users.json?login={}",
        "donor": "http://lims2/donors/info/details.json?external_donor_name={}&parent_specimens=true",
        "session": "http://lims2/ophys_sessions.json?id={}",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiUserSettings()
        self.ui.setupUi(self)
        self.connect_signals()
        config_fp = r"C:\Users\ariellel\repos\aind\aind-mesoscope-user-schema-ui\config.yml"
        with open(config_fp, "r") as file:
            self.config = yaml.safe_load(file)

    def connect_signals(self) -> None:
        """Connect signals to slots."""
        self.ui.submitPushButton.setEnabled(False)
        self.ui.submitPushButton.clicked.connect(self.submit_button_clicked)
        self.ui.userNameLineEdit.textChanged.connect(self.check_submit_button)
        self.ui.sessionIdLineEdit.textChanged.connect(self.check_submit_button)
        self.ui.subjectIdLineEdit.textChanged.connect(self.check_submit_button)

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
        return requests.get(self._LIMS_URLS[api].format(lims_entry))

    def _get_lims_project_code(self, lims_response: list) -> str:
        """Retrieves project code from LIMS response.

        Parameters
        ----------
        lims_response : list
            LIMS response.

        Returns
        -------
        str
            Project code.
        """
        print(f"Getting LIMS project code from response: {lims_response}")

    def submit_button_clicked(self) -> None:
        """Runs job to retrieve data from user inputs. If successful will drop a UserSettings.json in the acquisition directory."""
        print("Submit button clicked")
        user_name = self.ui.userNameLineEdit.text()
        session_id = self.ui.sessionIdLineEdit.text()
        subject_id = self.ui.subjectIdLineEdit.text()

        subject_id_response = self._get_lims_response(subject_id, "donor")
        try:
            assert subject_id_response.status_code == 200
        except AssertionError:
            self.ui.error_message.showMessage("Enter a valid subject ID")
            return
        session_response = self._get_lims_response(session_id, "session")
        try:
            assert session_response.status_code == 200
        except AssertionError:
            self.ui.error_message.showMessage("Session ID must be an integer")
            return
        # import pdb;pdb.set_trace()
        behavior_json = next(Path(self.config["behavior_dir"]).glob(f"{session_id}_Behavior*.json"))
        with open(behavior_json, "r") as j:
            behavior_data = json.load(j)
        start_time = behavior_data["RecordingReport"]["TimeStart"]
        end_time = behavior_data["RecordingReport"]["TimeEnd"]

        user_input = UserInput(
            input_source=self.config["acquisition_dir"],
            behavior_source=self.config["behavior_dir"],
            output_directory=self.config["output_dir"],
            session_start_time=start_time,
            session_end_time=end_time,
            subject_id=subject_id,
            project=session_response.json()[0]["project"]["code"],
            experimenter_full_name=[user_name],
        )
        user_input = user_input.dict()
        with open(
            Path(self.config["acquisition_dir"]) / session_id / "user_settings.json", "w"
        ) as j:
            json.dump(user_input, j, indent=4)
        self.ui.error_message.showMessage("User settings saved")
        self.ui.userNameLineEdit.clear()
        self.ui.sessionIdLineEdit.clear()
        self.ui.subjectIdLineEdit.clear()

    def check_submit_button(self) -> None:
        """Checks conditions to see if the submit button can be enabled."""
        if (
            self.ui.userNameLineEdit.text()
            and self.ui.sessionIdLineEdit.text()
            and self.ui.subjectIdLineEdit.text()
        ):
            self.ui.submitPushButton.setEnabled(True)
        else:
            self.ui.submitPushButton.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
