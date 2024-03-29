"""Example test template."""

from unittest.mock import MagicMock, patch, mock_open
import unittest
from aind_mesoscope_user_schema_ui.user_settings_ui import Widget
from requests import Response
import json
import sys
from PySide6.QtWidgets import QApplication

# What I want to test:
# Whether the submit button is enabled or disabled based on the 
# textChanged signal from the line edits.
# Test if the json outputs as expected
app = QApplication(sys.argv)


class UserSettingsTest(unittest.TestCase):
    """Example Test Class"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.user_name = "Radia Pearlman"
        cls.session_id = "1234567890"
        cls.subject_id = "900002"
        cls.user_name_bad = "Jareth"
        cls.session_id_bad = "0987654321"
        cls.subject_id_bad = "900001"
        cls.project = "mouse"
        cls.lims_response = [
            {
                "project": {"code": "omFISHSstMeso"},
                "specimen": {"external_specimen_name": "711914"},
            }
        ]
        cls.config = {
            "acquisition_dir": "D:\\mesoscope_data",
            "behavior_dir": "D:\\behavior",
            "output_dir": ".",
        }

    # mocked response borrowed from Jon Y. 
    #   https://github.com/AllenNeuralDynamics/aind-data-access-api/blob/f522f80a3a210abc276a565fd4e3fdb5d18068be/tests/test_document_db.py#L41
    @patch("os.getenv")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="{ \
           'acquisition_dir': 'D:\\mesoscope_data', \
            'output_dir': '.' \
            }",
    )
    @patch("requests.get")
    def test_lims_response(
        self,
        mock_get: MagicMock,
        mock_file_open: MagicMock,
        mock_env: MagicMock,
    ):
        """test lims response."""
        mock_env.return_value = "/path/config.yml"
        w = Widget()

        mock_response = Response()
        mock_response.status_code = 200
        body = json.dumps(self.lims_response)
        mock_response._content = body.encode("utf-8")
        mock_get.return_value = mock_response
        response = w._get_lims_response(self.session_id, "session")
        self.assertEqual(response.json(), self.lims_response)

        mock_response = Response()
        mock_response.status_code = 404
        body = json.dumps(None)
        mock_response._content = json.dumps({"body": body}).encode("utf-8")
        mock_get.return_value = mock_response
        response = w._get_lims_response(self.session_id_bad, "session")
        self.assertEqual(response.status_code, 404)
        w.close()

    @patch("os.getenv")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="{ \
           'acquisition_dir': 'D:\\mesoscope_data', \
            'output_dir': '.' \
            }",
    )
    def test_user_response(
        self,
        mock_file_open: MagicMock,
        mock_env: MagicMock,
    ):
        """Test user response"""
        mock_env.return_value = "/path/config.yml"
        w = Widget()

        good_response = w._check_user(self.user_name)
        bad_response = w._check_user(self.user_name_bad)
        self.assertEqual(good_response, True)
        self.assertEqual(bad_response, False)
        w.close()

    @patch("os.getenv")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="{ \
           'acquisition_dir': 'D:\\mesoscope_data', \
            'output_dir': '.' \
            }",
    )
    @patch("requests.get")
    def test_session_data(
        self,
        mock_get: MagicMock,
        mock_file_open: MagicMock,
        mock_env: MagicMock,
    ):
        """Test session data"""
        mock_env.return_value = "/path/config.yml"
        w = Widget()

        mock_response = Response()
        mock_response.status_code = 200
        body = json.dumps(self.lims_response)
        mock_response._content = body.encode("utf-8")
        mock_get.return_value = mock_response
        response = w._get_lims_response(self.session_id, "session")
        session_data = w._session_data(response)
        self.assertEqual(session_data, self.lims_response[0])

        w.close()


if __name__ == "__main__":
    unittest.main()
