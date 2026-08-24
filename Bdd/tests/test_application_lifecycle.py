import runpy
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from behave.parser import parse_file

from Bdd import application
from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.simulator.page import SimulatorPage
from autowork_core.runtime import scenario_runtime
from autowork_core.runtime.application_lifecycle import (
    ApplicationLifecyclePhase,
    callbacks_for,
    reset_application_lifecycle,
    restore_application_lifecycle,
    snapshot_application_lifecycle,
)
from autowork_core.runtime.behave_runner import temporary_settings


class ApplicationLifecycleTests(unittest.TestCase):
    def test_precise_phase_license_is_configured_before_start_and_restored(self):
        lifecycle_state = snapshot_application_lifecycle()
        reset_application_lifecycle()
        try:
            step_path = (
                Path(__file__).resolve().parents[1]
                / "steps/APS_steps/Console-SRS.22787.py"
            )
            namespace = runpy.run_path(str(step_path))
            feature_path = (
                Path(__file__).resolve().parents[1]
                / "test_features/APS_features/Console-SRS.22787.feature"
            )
            scenarios = list(parse_file(str(feature_path)).walk_scenarios())
            before_callbacks = [
                [
                    item.callback.__name__
                    for item in callbacks_for(
                        ApplicationLifecyclePhase.BEFORE_APP_START,
                        scenario,
                    )
                ]
                for scenario in scenarios
            ]
            self.assertEqual(
                [
                    ["configure_license_with_precise_phase"],
                    ["configure_license_without_precise_phase"],
                    ["configure_license_with_precise_phase"],
                    ["configure_license_with_precise_phase"],
                ],
                before_callbacks,
            )
            self.assertTrue(all(
                [item.callback.__name__ for item in callbacks_for(
                    ApplicationLifecyclePhase.AFTER_APP_STOP,
                    scenario,
                )] == ["restore_license_configuration"]
                for scenario in scenarios
            ))
            context = SimpleNamespace(
                autowork_run=SimpleNamespace(public_data={
                    "ad_and_abs_key": "supported-key",
                    "not_ad_and_abs_key": "unsupported-key",
                }),
            )
            with TemporaryDirectory() as root:
                key_path = Path(root) / "key"
                key_path.write_text("initial", encoding="utf-8")
                namespace["_write_license_key"].__globals__["_LICENSE_KEY_PATH"] = (
                    key_path
                )

                namespace["configure_license_without_precise_phase"](
                    context,
                    None,
                )
                self.assertEqual(
                    "unsupported-key",
                    key_path.read_text(encoding="utf-8"),
                )
                namespace["given_supported_precise_phase_license_is_not_used"](
                    context,
                )

                namespace["configure_license_with_precise_phase"](
                    context,
                    None,
                )
                self.assertEqual(
                    "supported-key",
                    key_path.read_text(encoding="utf-8"),
                )
                namespace["given_supported_precise_phase_license_is_used"](
                    context,
                )

                key_path.write_text("unsupported-key", encoding="utf-8")
                namespace["restore_license_configuration"](context, None)
                self.assertEqual(
                    "supported-key",
                    key_path.read_text(encoding="utf-8"),
                )
        finally:
            restore_application_lifecycle(lifecycle_state)

    def test_application_import_does_not_load_project_pages(self):
        repository_root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                (
                    "import sys; import Bdd.application; "
                    "names={'Bdd.page_obj.patient.page', "
                    "'Bdd.page_obj.simulator.page'}; "
                    "loaded=sorted(names & set(sys.modules)); "
                    "assert not loaded, loaded"
                ),
            ],
            cwd=repository_root,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)

    def test_starts_simulator_only_for_auto_gantry_scenario(self):
        context, gantry_scenario = self._scenario_context("GANTRY")
        _context, plain_scenario = self._scenario_context()
        page = Mock()
        page.wait_until_open.return_value = True
        with (
            patch.object(application, "sleep") as sleep,
            patch.object(application, "start_simulator") as simulator,
            patch.object(application, "get_page", return_value=page),
        ):
            with temporary_settings(app_launch_mode="auto"):
                application.prepare_scenario(context, gantry_scenario)
            with temporary_settings(app_launch_mode="attach"):
                application.prepare_scenario(context, gantry_scenario)
            with temporary_settings(app_launch_mode="auto"):
                application.prepare_scenario(context, plain_scenario)

        sleep.assert_called_once_with(1)
        simulator.assert_called_once_with()

    def test_attach_mode_is_read_by_project_hook(self):
        context, scenario = self._scenario_context("gantry")
        simulator = Mock()
        simulator.initialize.return_value = simulator

        with (
            patch.object(
                application,
                "get_page",
                return_value=simulator,
            ),
            patch.object(application, "start_simulator") as start,
            temporary_settings(app_launch_mode="attach"),
        ):
            scenario_runtime.prepare_project_scenario(context, scenario)

        start.assert_not_called()
        simulator.initialize.assert_called_once_with(
            auto_mode=False,
            timeout=60,
        )

    def test_patient_readiness_uses_window_root_and_fails_closed(self):
        context, scenario = self._scenario_context()
        patient = Mock()
        patient.wait_until_open.return_value = False

        with patch.object(
                application,
                "get_page",
                return_value=patient,
        ) as get_page:
            with self.assertRaisesRegex(
                    TimeoutError,
                    "Patient window.yaml did not open",
            ):
                with temporary_settings(app_launch_mode="auto"):
                    application.prepare_scenario(context, scenario)

        get_page.assert_called_once_with(context, PatientPage)
        patient.wait_until_open.assert_called_once_with(timeout=30)

    def test_patient_window_root_must_be_continuously_ready(self):
        patient = object.__new__(PatientPage)
        patient.wait_exposed = Mock(
            side_effect=[True, False, True, True, True],
        )
        clock = [0.0]

        with (
            patch(
                "Bdd.page_obj.patient.page.time.monotonic",
                side_effect=lambda: clock[0],
            ),
            patch(
                "Bdd.page_obj.patient.page.time.sleep",
                side_effect=lambda seconds: clock.__setitem__(
                    0,
                    clock[0] + seconds,
                ),
            ),
        ):
            ready = patient.wait_until_main_page_ready(
                timeout=10,
                stable_for=1,
                interval=0.5,
            )

        self.assertTrue(ready)
        self.assertEqual(5, patient.wait_exposed.call_count)
        patient.wait_exposed.assert_called_with(
            "$Patient_window",
            timeout=0,
        )

    def test_patient_main_page_cannot_become_ready_after_deadline(self):
        patient = object.__new__(PatientPage)
        patient.wait_exposed = Mock(return_value=True)

        with (
            patch(
                "Bdd.page_obj.patient.page.time.monotonic",
                side_effect=[0.0, 0.5, 1.1],
            ),
            patch("Bdd.page_obj.patient.page.time.sleep"),
        ):
            ready = patient.wait_until_main_page_ready(
                timeout=1,
                stable_for=0.5,
                interval=0.5,
            )

        self.assertFalse(ready)
        self.assertEqual(2, patient.wait_exposed.call_count)

    def test_auto_gantry_initializes_simulator_page(self):
        events = []
        context, scenario = self._scenario_context("gantry")
        simulator = Mock()
        simulator.initialize.side_effect = (
            lambda **kwargs: events.append(
                f"simulator-initialized:{kwargs['auto_mode']}:{kwargs['timeout']}"
            )
            or simulator
        )
        patient = Mock()
        patient.wait_until_open.return_value = True

        def page(_context, page_class):
            return {
                SimulatorPage: simulator,
                PatientPage: patient,
            }[page_class]

        with (
            patch.object(application, "sleep"),
            patch.object(application, "start_simulator"),
            patch.object(
                application,
                "get_page",
                side_effect=page,
            ) as get_page,
        ):
            with temporary_settings(app_launch_mode="auto"):
                application.prepare_scenario(context, scenario)
            self.assertIs(simulator, context.autowork_scenario.simulator)

        self.assertEqual(
            [
                call(context, SimulatorPage),
                call(context, PatientPage),
            ],
            get_page.call_args_list,
        )
        simulator.initialize.assert_called_once_with(
            auto_mode=True,
            timeout=60,
        )
        patient.wait_until_open.assert_called_once_with(timeout=30)
        self.assertEqual(["simulator-initialized:True:60"], events)

    def test_auto_gantry_closes_page_when_initialization_fails(self):
        context, scenario = self._scenario_context("gantry")
        simulator = Mock()
        simulator.initialize.side_effect = TimeoutError(
            "Simulator unavailable"
        )

        with (
            patch.object(application, "sleep"),
            patch.object(application, "start_simulator"),
            patch.object(
                application,
                "get_page",
                return_value=simulator,
            ),
        ):
            with self.assertRaisesRegex(TimeoutError, "Simulator unavailable"):
                with temporary_settings(app_launch_mode="auto"):
                    application.prepare_scenario(context, scenario)

        simulator.close.assert_called_once_with()
        self.assertIsNone(context.autowork_scenario.simulator)

    def test_attach_gantry_initializes_page_without_auto_mode(self):
        events = []
        context, scenario = self._scenario_context("gantry")
        simulator = Mock()
        simulator.initialize.side_effect = (
            lambda **kwargs: events.append(
                f"simulator-initialized:{kwargs['auto_mode']}:{kwargs['timeout']}"
            )
            or simulator
        )

        with patch.object(
                application,
                "get_page",
                return_value=simulator,
        ):
            with temporary_settings(app_launch_mode="attach"):
                application.prepare_scenario(context, scenario)

        simulator.initialize.assert_called_once_with(
            auto_mode=False,
            timeout=60,
        )
        self.assertEqual(
            ["simulator-initialized:False:60"],
            events,
        )

    def test_cleanup_closes_and_clears_simulator_page_once(self):
        context, scenario = self._scenario_context("gantry")
        simulator = Mock()
        context.autowork_scenario.simulator = simulator

        application.cleanup_scenario(context, scenario)
        application.cleanup_scenario(context, scenario)

        simulator.close.assert_called_once_with()
        self.assertIsNone(context.autowork_scenario.simulator)

    @staticmethod
    def _scenario_context(*tags):
        return (
            SimpleNamespace(
                autowork_scenario=scenario_runtime.ScenarioRuntimeState(),
            ),
            SimpleNamespace(
                name="Lifecycle scenario",
                tags=tags,
                effective_tags=tags,
            ),
        )


if __name__ == "__main__":
    unittest.main()