import time

from autowork_core.page import WindowPage


class PatientPage(WindowPage):
    root_locator_file = "patient/window.yaml"
    root_locator = "Patient_window"

    def wait_until_main_page_ready(
            self,
            timeout=30,
            stable_for=3,
            interval=0.5,
    ) -> bool:
        deadline = time.monotonic() + max(float(timeout or 0), 0)
        stable_for = max(float(stable_for or 0), 0)
        interval = max(float(interval or 0), 0.05)
        stable_since = None

        while True:
            # ready = self.wait_exposed("$Anonymous_button", timeout=0)
            ready = self.wait_exposed("$Patient_window", timeout=0)
            now = time.monotonic()
            if now > deadline:
                return False
            if ready:
                if stable_since is None:
                    stable_since = now
                if now - stable_since >= stable_for:
                    return True
            else:
                stable_since = None

            if now >= deadline:
                return False
            time.sleep(min(interval, max(0, deadline - now)))

    def register_patient_for_step_and_shoot(self) -> None:
        self.click("$Anonymous_button")
        self.click("$Exam_Application_Yes_button")
        self.click("$radioAdult_button")
        self.click("$show_select_posture_button")
        self.click("$select_posture1_button")
        self.click("$Reference_Exam_Cards_button")
        self.click("$cardiac_button")
        self.click("$Step_and_Shoot_button")
        self.save_attr('$patient_id_edit','Value.Value','patient_id')
        self.click("$ok_Button")

    def register_patient_for_coronary_cta(self) -> None:
        self.click("$Anonymous_button")
        self.click("$Exam_Application_Yes_button")
        self.click("$radioAdult_button")
        self.click("$show_select_posture_button")
        self.click("$select_posture1_button")
        self.click("$Reference_Exam_Cards_button")
        self.click("$cardiac_button")
        self.click("$Coronary_CTA_button")
        self.save_attr('$patient_id_edit','Value.Value','patient_id')
        self.click("$ok_Button")

    def register_patient_for_gated_helical_cta(self) -> None:
        self.click("$Anonymous_button")
        self.click("$Exam_Application_Yes_button")
        self.click("$radioAdult_button")
        self.click("$show_select_posture_button")
        self.click("$select_posture1_button")
        self.click("$Reference_Exam_Cards_button")
        self.click("$Thorax_button")
        self.click("$Gated_Helical_CTA_button")
        self.save_attr('$patient_id_edit','Value.Value','patient_id')
        self.click("$ok_Button")