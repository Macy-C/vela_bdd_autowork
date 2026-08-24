from Bdd.page_obj.plan.acquisition import Acquisition
from Bdd.page_obj.plan.all_parameters import AllParametersView
from autowork_core.page import WindowPage


class PlanPage(WindowPage):
    root_locator_file = "plan/plan_locator.yaml"
    root_locator = "ExamApplication_window"

    @property
    def all_parameters(self) -> AllParametersView:
        return self.get_view(AllParametersView)

    @property
    def acquisition(self) -> Acquisition:
        return self.get_view(Acquisition)

    def open_all_parameters(self) -> None:
        self.click("$show_all_button")

    def select_step_and_shoot_ax(self) -> None:
        self.click("$step_and_shoot_Ax")
