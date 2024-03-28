"""Example test template."""

import unittest

# What I want to test:
# Whether the submit button is enabled or disabled based on the textChanged signal from the line edits.
# Test if the json outputs as expected

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

    def test_name_input(self):
        """Example of how to test the truth of a statement."""

        self.assertTrue(1 == 1)


if __name__ == "__main__":
    unittest.main()
