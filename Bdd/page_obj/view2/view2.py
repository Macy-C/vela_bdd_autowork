from Bdd.page_obj.view2.image_parameters import ImageParameters
from autowork_core.page import WindowView, WindowPage

class View2(WindowPage):
    root_locator_file = "view2/window.yaml"
    root_locator = "ExamApplication_window"

    @property
    def image_parameters(self) -> ImageParameters:
        return self.get_view(ImageParameters)