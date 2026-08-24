import runpy
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from Bdd.page_obj.log_viewer.page import LogViewerPage
from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
from Bdd.page_obj.simulator.page import SimulatorPage
from autowork_core.common.root_store import RootStore
from autowork_core.common.variables import Stratify
from autowork_core.page import get_page


class PageObjectMigrationTests(unittest.TestCase):
    def setUp(self):
        self.context = SimpleNamespace(
            autowork_feature=SimpleNamespace(
                pages={},
                locators=Stratify(),
                data=Stratify(),
            ),
            autowork_scenario=SimpleNamespace(
                pages={},
                windows=RootStore(),
            ),
        )

    def test_window_pages_load_real_isolated_locator_packages(self):
        cases = (
            (PatientPage, "patient_window"),
            (PlanPage, "examapplication_window"),
            (SimulatorPage, "simulator_window"),
            (LogViewerPage, "log_viewer_window"),
        )

        for page_class, expected_root in cases:
            with self.subTest(page=page_class.__name__):
                page = get_page(self.context, page_class)
                self.assertEqual(expected_root, page.window_root_name)
                self.assertIn(expected_root, page._window_locators)
                self.assertIsNone(
                    self.context.autowork_feature.locators[expected_root]
                )

        patient = get_page(self.context, PatientPage)
        posture = patient.get_locator("$select_posture1_button")
        self.assertEqual("patient_window", posture.region_name)

    def test_all_parameters_view_is_cached_and_rechecks_activation(self):
        plan = get_page(self.context, PlanPage)
        plan.wait_visible = Mock(return_value=True)

        first = plan.all_parameters
        second = plan.all_parameters

        self.assertIs(first, second)
        self.assertEqual(2, plan.wait_visible.call_count)
        plan.wait_visible.assert_called_with(
            "$all_parameters_window",
            timeout=10,
        )
        self.assertEqual(
            "examapplication_window",
            first.get_locator("$absolute_button").root_name,
        )
        self.assertEqual(
            "examapplication_window",
            first.get_locator("$ecg_relative_phase_ComboBox").root_name,
        )

    def test_scan_step_preserves_original_cross_window_sequence(self):
        namespace = _load_step_file("Console-SRS.22774.py")
        calls = Mock()
        plan = Mock()
        simulator = Mock()
        sleep = Mock()
        calls.attach_mock(plan, "plan")
        calls.attach_mock(simulator, "simulator")
        calls.attach_mock(sleep, "sleep")
        simulator.ensure_ecg_on.return_value = True
        plan.wait_visible.return_value = True
        plan.wait_ready.return_value = True
        target = namespace["when_click_go_on_display_interface"]
        target.__globals__["get_page"] = Mock(side_effect=lambda _context, page_cls: {
            PlanPage: plan,
            SimulatorPage: simulator,
        }[page_cls])
        target.__globals__["sleep"] = sleep

        target(object())

        self.assertEqual(
            [
                call.simulator.unset_window_topmost("$Simulator_window"),
                call.simulator.bring_to_front(
                    "$Simulator_window",
                    activate=True,
                ),
                call.simulator.bring_to_front(
                    "$Simulator_window",
                    activate=True,
                ),
                call.simulator.ensure_ecg_on(),
                call.plan.wait_visible("$MessageBox_window", timeout=8),
                call.plan.click("$MessageBox_OK_button"),
                call.simulator.minimize_window("$Simulator_window"),
                call.plan.click("$go_scan_button"),
                call.plan.wait_enabled("$Cancel_scan_button"),
                call.simulator.bring_to_front(
                    "$Simulator_window",
                    activate=True,
                ),
                call.plan.wait_visible("$MessageBox_window", timeout=5),
                call.plan.click("$MessageBox_OK_button"),
                call.simulator.wait_ready("$Simulator_window"),
                call.sleep(0.5),
                call.simulator.start_auto_scan(),
                call.sleep(20),
                call.simulator.minimize_window("$Simulator_window"),
                call.plan.wait_enabled("$go_scan_button", timeout=20),
                call.plan.click("$go_scan_button"),
                call.plan.wait_enabled("$Cancel_scan_button"),
                call.simulator.bring_to_front(
                    "$Simulator_window",
                    activate=True,
                ),
                call.sleep(0.5),
                call.simulator.start_manual_scan(),
                call.sleep(3),
                call.simulator.minimize_window("$Simulator_window"),
                call.sleep(2),
                call.plan.click("$legacy_scan_transition_position"),
                call.plan.click("$step_and_shoot_Ax"),
                call.plan.click("$go_scan_button"),
                call.plan.wait_ready(
                    "$Dose_Notification_confirm_button",
                    timeout=5,
                ),
                call.plan.click("$Dose_Notification_confirm_button"),
                call.plan.click("$go_scan_button"),
                call.plan.wait_enabled("$Cancel_scan_button"),
                call.simulator.bring_to_front(
                    "$Simulator_window",
                    activate=True,
                ),
                call.sleep(0.5),
                call.simulator.start_auto_scan(wait_type="exists"),
                call.sleep(3),
                call.simulator.minimize_window("$Simulator_window"),
                call.plan.click("$start_scan_button"),
                call.sleep(1),
                call.simulator.minimize_window("$Simulator_window"),
                call.sleep(5),
            ],
            calls.mock_calls,
        )

    def test_simulator_ensure_ecg_on_is_idempotent(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator.wait_visible = Mock(return_value=True)
        simulator.click = Mock()
        simulator.assert_visible = Mock()

        changed = simulator.ensure_ecg_on()

        self.assertFalse(changed)
        simulator.wait_visible.assert_called_once_with(
            "$ECG_Off_button",
            timeout=0,
        )
        simulator.click.assert_not_called()
        simulator.assert_visible.assert_not_called()

    def test_simulator_ensure_ecg_on_switches_and_verifies(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator.wait_visible = Mock(side_effect=[False, True])
        simulator.click = Mock()
        simulator.assert_visible = Mock()

        changed = simulator.ensure_ecg_on()

        self.assertTrue(changed)
        self.assertEqual(
            [
                call("$ECG_Off_button", timeout=0),
                call("$ECG_On_button", timeout=2),
            ],
            simulator.wait_visible.call_args_list,
        )
        simulator.click.assert_called_once_with("$ECG_On_button")
        simulator.assert_visible.assert_called_once_with(
            "$ECG_Off_button",
            timeout=5,
        )

    def test_simulator_ensure_ecg_on_rejects_unknown_state(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator.wait_visible = Mock(return_value=False)
        simulator.click = Mock()

        with self.assertRaisesRegex(RuntimeError, "determine the ECG state"):
            simulator.ensure_ecg_on()

        simulator.click.assert_not_called()

    def test_simulator_ensure_ecg_off_is_idempotent(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator.wait_visible = Mock(return_value=True)
        simulator.click = Mock()
        simulator.assert_visible = Mock()

        changed = simulator.ensure_ecg_off()

        self.assertFalse(changed)
        simulator.wait_visible.assert_called_once_with(
            "$ECG_On_button",
            timeout=0,
        )
        simulator.click.assert_not_called()
        simulator.assert_visible.assert_not_called()

    def test_simulator_ensure_ecg_off_switches_and_verifies(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator.wait_visible = Mock(side_effect=[False, True])
        simulator.click = Mock()
        simulator.assert_visible = Mock()

        changed = simulator.ensure_ecg_off()

        self.assertTrue(changed)
        self.assertEqual(
            [
                call("$ECG_On_button", timeout=0),
                call("$ECG_Off_button", timeout=2),
            ],
            simulator.wait_visible.call_args_list,
        )
        simulator.click.assert_called_once_with("$ECG_Off_button")
        simulator.assert_visible.assert_called_once_with(
            "$ECG_On_button",
            timeout=5,
        )

    def test_simulator_ensure_ecg_off_rejects_unknown_state(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator.wait_visible = Mock(return_value=False)
        simulator.click = Mock()

        with self.assertRaisesRegex(RuntimeError, "determine the ECG state"):
            simulator.ensure_ecg_off()

        simulator.click.assert_not_called()

    def test_simulator_delegates_common_gantry_api_operations(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        gantry = Mock()
        gantry.get_gantry_door_switch_state.return_value = "closed"
        gantry.couch_speed = 4
        simulator._gantry = gantry

        simulator.close_gantry_estop()
        simulator.enable_gantry()
        simulator.pause_gantry()
        simulator.start_auto_scan_via_api()
        simulator.start_manual_scan_via_api()
        simulator.zero_couch()
        simulator.restart_gantry_rotor()
        simulator.unload_patient()
        simulator.move_couch_horizontal_to_position(
            move_out=True,
            position=120,
        )
        simulator.move_couch_vertical_to_position(
            move_up=False,
            position=80,
            relative=True,
        )
        speed = simulator.couch_speed
        simulator.couch_speed = 6
        state = simulator.get_gantry_door_switch_state()

        self.assertEqual(
            [
                call.close_gantry_estop(),
                call.enable_gantry(),
                call.pause_gantry(),
                call.auto_start_scans(),
                call.manual_start_scans(),
                call.zero_couch(),
                call.restart_gantry_rotor(),
                call.couch_patient_unload(),
                call.move_couch_horizontal_to_position(True, 120, False),
                call.move_couch_vertical_to_position(False, 80, True),
                call.get_gantry_door_switch_state(),
            ],
            gantry.mock_calls,
        )
        self.assertEqual(4, speed)
        self.assertEqual(6, gantry.couch_speed)
        self.assertEqual("closed", state)

    def test_simulator_rejects_missing_gantry_api(self):
        simulator = SimulatorPage.__new__(SimulatorPage)

        with self.assertRaisesRegex(RuntimeError, "not initialized"):
            simulator.close_gantry_estop()

    def test_simulator_operational_wait_fails_closed(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator.wait_until_open = Mock(return_value=False)

        with self.assertRaisesRegex(TimeoutError, "did not become ready"):
            simulator.wait_until_operational(timeout=60)

        simulator.wait_until_open.assert_called_once_with(timeout=60)

    @patch("Bdd.page_obj.simulator.page.GantryEasyControl")
    def test_simulator_auto_initialization_owns_control(self, gantry_type):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator._gantry = None
        simulator.wait_until_operational = Mock(return_value=simulator)

        result = simulator.initialize(auto_mode=True, timeout=45)

        self.assertIs(simulator, result)
        simulator.wait_until_operational.assert_called_once_with(timeout=45)
        gantry_type.assert_called_once_with()
        gantry_type.return_value.close_gantry_estop.assert_called_once_with()

    @patch("Bdd.page_obj.simulator.page.GantryEasyControl")
    def test_simulator_attach_initialization_does_not_change_ui_state(
            self,
            gantry_type,
    ):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator._gantry = None
        simulator.wait_until_operational = Mock()

        simulator.initialize(auto_mode=False)

        simulator.wait_until_operational.assert_not_called()
        gantry_type.assert_called_once_with()
        gantry_type.return_value.close_gantry_estop.assert_not_called()

    @patch("Bdd.page_obj.simulator.page.GantryEasyControl")
    def test_simulator_initialization_failure_releases_control(
            self,
            gantry_type,
    ):
        simulator = SimulatorPage.__new__(SimulatorPage)
        simulator._gantry = None
        simulator.wait_until_operational = Mock(return_value=simulator)
        gantry_type.return_value.close_gantry_estop.side_effect = RuntimeError(
            "estop failed"
        )

        with self.assertRaisesRegex(RuntimeError, "estop failed"):
            simulator.initialize(auto_mode=True)

        gantry_type.return_value.close.assert_called_once_with()
        self.assertIsNone(simulator._gantry)

    def test_simulator_close_is_idempotent(self):
        simulator = SimulatorPage.__new__(SimulatorPage)
        gantry = Mock()
        simulator._gantry = gantry

        simulator.close()
        simulator.close()

        gantry.close.assert_called_once_with()

    def test_absolute_tolerance_step_preserves_phase_unit_commit(self):
        namespace = _load_step_file("Console-SRS.22774.py")
        plan = Mock()
        parameters = Mock()
        plan.all_parameters = parameters
        target = namespace["when_phase_tolerance_is_set"]
        target.__globals__["get_page"] = Mock(return_value=plan)

        target(object(), "100 ms")

        self.assertEqual(
            [
                call.input_text(
                    "$absolute_Phase_tolerance_edit_box",
                    "100",
                ),
                call.click("$absolute_Phase_unit_ocr"),
            ],
            parameters.mock_calls,
        )

    def test_reconstruction_range_step_preserves_absolute_branch(self):
        namespace = _load_step_file("Console-SRS.22777.py")
        plan = Mock()
        parameters = Mock()
        parameters.get_text.return_value = ["Precise Phase", "250", "450"]
        plan.all_parameters = parameters
        target = namespace["then_reconstruction_phase_range_shown"]
        target.__globals__["get_page"] = Mock(return_value=plan)

        target(object(), "250 to 450")

        parameters.expand_dropdown.assert_called_once_with(
            "$ecg_absolute_phase_ComboBox"
        )
        parameters.get_text.assert_called_once_with(
            "$ecg_absolute_phase_list",
            first_only=False,
        )

    def test_relative_tolerance_step_preserves_original_action_order(self):
        namespace = _load_step_file("relative_step.py", relative=True)
        plan = Mock()
        parameters = Mock()
        plan.all_parameters = parameters
        target = namespace["when_phase_tolerance_is_set"]
        target.__globals__["get_page"] = Mock(return_value=plan)

        target(object(), "75 ms")

        self.assertEqual(
            [
                call.input_text("$absolute_Phase_edit_box", 350),
                call.input_text(
                    "$absolute_Phase_tolerance_edit_box",
                    "75",
                ),
                call.click("$absolute_Phase_unit_ocr"),
            ],
            parameters.mock_calls,
        )


def _load_step_file(file_name, *, relative=False):
    def identity_decorator(_pattern):
        return lambda function: function

    project_root = Path(__file__).resolve().parents[2]
    path = project_root / "Bdd" / "steps"
    if not relative:
        path /= "Absolute_delay_steps"
    path /= file_name
    with patch.multiple(
        "behave",
        given=identity_decorator,
        when=identity_decorator,
        then=identity_decorator,
        step=identity_decorator,
    ):
        return runpy.run_path(str(path))
if __name__ == "__main__":
    unittest.main()
