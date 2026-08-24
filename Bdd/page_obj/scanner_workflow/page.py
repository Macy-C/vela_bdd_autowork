from autowork_core.page import WindowPage


class ScannerWorkflowPage(WindowPage):
    root_locator_file = "scanner_workflow/window.yaml"
    root_locator = "scannerworkflowuiform_window"

    def open_home(self):
        self.click("$home_button")