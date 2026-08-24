import unittest
from pathlib import Path

from Bdd.integrations.gantry.easy_control import DEFAULT_DLL_DIR


class GantryIntegrationTests(unittest.TestCase):
    def test_managed_dependencies_are_colocated_with_project_integration(self):
        expected = (
            Path(__file__).resolve().parents[1]
            / "integrations"
            / "gantry"
            / "bin"
        )

        self.assertEqual(expected, DEFAULT_DLL_DIR)
        self.assertEqual(
            {
                "CANMS_Converter.dll",
                "CanmsTypes.dll",
                "GantryEasyControl.dll",
                "GantryINFUtilities.dll",
                "Interop.CANMSENGINELib.dll",
            },
            {path.name for path in DEFAULT_DLL_DIR.glob("*.dll")},
        )


if __name__ == "__main__":
    unittest.main()