from Bdd.page_obj.patient_directory.preferences import Preferences
from Bdd.page_obj.patient_directory.quick_review import QuickReviewPage
from autowork_core.page import WindowPage


class PatientDirectory(WindowPage):
    root_locator_file = "patient_directory/window.yaml"
    root_locator = "Patient_Directory_window"

    @property
    def preferences(self) -> Preferences:
        return self.get_view(Preferences)
    @property
    def quick_review(self) -> QuickReviewPage:
        return self.get_view(QuickReviewPage)

    def wait_main_window_ready(self):
        self.wait_ready('$Patient_Directory_window', timeout=10)

    def open_preferences_window(self):
        self.click('$Preferences_button')


