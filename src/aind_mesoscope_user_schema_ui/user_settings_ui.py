# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtCore import QMetaMethod
from PySide6.QtWidgets import QApplication, QWidget

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py
from ui.ui_form import UiUserSettings

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiUserSettings()
        self.ui.setupUi(self)
        self.connect_signals()
    
    def connect_signals(self) -> None:
        """Connect signals to slots.
        """
        self.submitPushButton.setEnabled(False)
        self.submitPushButton.clicked.connect(self.submit_button_clicked)
        self.userNameLineEdit.textChanged.connect(self.check_submit_button)
        self.sessionIdLineEdit.textChanged.connect(self.check_submit_button)
        self.experimentIdLineEdit.textChanged.connect(self.check_submit_button)
    
    def _verify_lims_entry(self, lims_entry: str) -> bool:
        """Verify LIMS entry.

        Parameters
        ----------
        lims_entry : str
            LIMS entry.
        
        Returns
        -------
        bool
        """
        print(f"Verifying LIMS entry: {lims_entry}")
        return True
    
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
        """Runs job to retrieve data from user inputs. If successful will drop a UserSettings.json in the acquisition directory.
        """
        print("Submit button clicked")
    
    def check_submit_button(self) -> None:
        """Checks conditions to see if the submit button can be enabled.
        """
        print("Checking submit button")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
