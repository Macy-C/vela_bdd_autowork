from autowork_core.page import WindowView


class ScanParametersView(WindowView):
    locator_file = "exam_card_manager/scan_parameters.yaml"
    active_locator = None

    def set_scan_type(self, scan_type: str) -> None:
        self.select_dropdown_option("$scan_type_combo", scan_type)
