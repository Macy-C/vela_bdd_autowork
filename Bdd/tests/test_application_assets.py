import unittest
from pathlib import Path


class ApplicationAssetTests(unittest.TestCase):
    def test_legacy_application_scripts_are_archived_under_bdd(self):
        script_dir = (
            Path(__file__).resolve().parents[1]
            / "resources"
            / "application"
            / "legacy-scripts"
        )

        self.assertEqual(
            {
                "StartApplication.bat": 688,
                "StartSimulator.bat": 857,
                "StopApplication.bat": 3774,
            },
            {
                path.name: path.stat().st_size
                for path in script_dir.glob("*.bat")
            },
        )


if __name__ == "__main__":
    unittest.main()