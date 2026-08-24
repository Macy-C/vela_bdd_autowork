from autowork_core.page import WindowView


class ClinicalSequenceView(WindowView):
    locator_file = "exam_card_manager/clinical_sequence.yaml"
    active_locator = None

    def select_step_and_shoot_ax(self):
        self.click("$step_and_shoot_ax_sequence")