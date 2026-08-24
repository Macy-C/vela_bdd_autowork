from autowork_core.page import WindowPage


class SwitchScreenPage(WindowPage):
    root_locator_file = "switch_screen/window.yaml"
    root_locator = "switch_screen_window"

    def toggle_screen(self):
        self.click("$toggle_screen_button")