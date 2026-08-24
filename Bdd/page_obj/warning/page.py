from autowork_core.page import WindowPage


class WarningPage(WindowPage):
    root_locator_file = "warning/window.yaml"
    root_locator = "warning_window"

    def click_ok_button(self) -> None:
        self.click("$warning_ok_button")
