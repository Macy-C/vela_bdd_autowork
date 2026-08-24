from Bdd.page_obj.plan.acquisition import Acquisition
from Bdd.page_obj.plan.all_parameters import AllParametersView
from Bdd.page_obj.plan.view import View
from autowork_core.page import WindowPage


class PlanPage(WindowPage):
    root_locator_file = "plan/window.yaml"
    root_locator = "ExamApplication_window"

    @property
    def all_parameters(self) -> AllParametersView:
        return self.get_view(AllParametersView)

    @property
    def acquisition(self) -> Acquisition:
        return self.get_view(Acquisition)

    @property
    def view(self) -> View:
        return self.get_view(View)

    def open_all_parameters(self) -> None:
        self.click("$show_all_button")

    def select_step_and_shoot_ax(self) -> None:
        self.click("$step_and_shoot_Ax")
