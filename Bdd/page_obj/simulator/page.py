from __future__ import annotations

from autowork_core.page import WindowPage
from Bdd.integrations.gantry import GantryEasyControl


class SimulatorPage(WindowPage):
    root_locator_file = "simulator/window.yaml"
    root_locator = "Simulator_window"

    def __init__(self, context):
        super().__init__(context)
        self._gantry = None

    def wait_until_operational(self, timeout=60):
        if not self.wait_until_open(timeout=timeout):
            raise TimeoutError(
                f"Simulator window.yaml did not become ready within {timeout} seconds"
            )
        return self

    def initialize(self, *, auto_mode: bool, timeout=60):
        if self._gantry is not None:
            return self
        if auto_mode:
            self.wait_until_operational(timeout=timeout)

        self._gantry = GantryEasyControl()
        try:
            if auto_mode:
                self.close_gantry_estop()
        except Exception:
            self.close()
            raise
        return self

    def close(self) -> None:
        gantry = self._gantry
        self._gantry = None
        if gantry is not None:
            gantry.close()

    def ensure_ecg_on(self) -> bool:
        if self.wait_visible("$ECG_Off_button", timeout=0):
            return False
        if not self.wait_visible("$ECG_On_button", timeout=2):
            raise RuntimeError("Unable to determine the ECG state")

        self.click("$ECG_On_button")
        self.assert_visible("$ECG_Off_button", timeout=5)
        return True

    def ensure_ecg_off(self) -> bool:
        if self.wait_visible("$ECG_On_button", timeout=0):
            return False
        if not self.wait_visible("$ECG_Off_button", timeout=2):
            raise RuntimeError("Unable to determine the ECG state")

        self.click("$ECG_Off_button")
        self.assert_visible("$ECG_On_button", timeout=5)
        return True

    def start_auto_scan(self, *, wait_type="visible") -> None:
        self.click("$Auto_scan_button", wait_type=wait_type)

    def start_manual_scan(self) -> None:
        self.click("$Manual_scan_button")

    def close_gantry_estop(self) -> None:
        self._require_gantry().close_gantry_estop()

    def enable_gantry(self) -> None:
        self._require_gantry().enable_gantry()

    def pause_gantry(self) -> None:
        self._require_gantry().pause_gantry()

    def start_auto_scan_via_api(self) -> None:
        self._require_gantry().auto_start_scans()

    def start_manual_scan_via_api(self) -> None:
        self._require_gantry().manual_start_scans()

    def zero_couch(self) -> None:
        self._require_gantry().zero_couch()

    def restart_gantry_rotor(self) -> None:
        self._require_gantry().restart_gantry_rotor()

    def unload_patient(self) -> None:
        self._require_gantry().couch_patient_unload()

    def move_couch_horizontal_to_position(
            self,
            *,
            move_out: bool,
            position: int,
            relative: bool = False,
    ) -> None:
        self._require_gantry().move_couch_horizontal_to_position(
            move_out,
            position,
            relative,
        )

    def move_couch_vertical_to_position(
            self,
            *,
            move_up: bool,
            position: int,
            relative: bool = False,
    ) -> None:
        self._require_gantry().move_couch_vertical_to_position(
            move_up,
            position,
            relative,
        )

    @property
    def couch_speed(self) -> int:
        return self._require_gantry().couch_speed

    @couch_speed.setter
    def couch_speed(self, value: int) -> None:
        self._require_gantry().couch_speed = value

    def get_gantry_door_switch_state(self):
        return self._require_gantry().get_gantry_door_switch_state()

    def _require_gantry(self) -> GantryEasyControl:
        gantry = getattr(self, "_gantry", None)
        if gantry is None:
            raise RuntimeError("GantryEasyControl is not initialized")
        return gantry