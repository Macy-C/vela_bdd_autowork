from autowork_core.page import WindowPage


class HomePage(WindowPage):
    root_locator_file = "home/window.yaml"
    root_locator = "home_window"

    def open_exam_card_manager(self):
        self.click("$exam_card_manager_entry")